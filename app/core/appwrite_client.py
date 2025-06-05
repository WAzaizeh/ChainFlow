from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query
from datetime import datetime
from .config import settings
from models.task import Task, SubTask
from models.checkins import Checkin
import uuid
import json

def make_client(authenticated=True) -> Client:
    """Creates an Appwrite client instance."""
    client = (
        Client()
        .set_endpoint(settings.APPWRITE_ENDPOINT)
        .set_project(settings.APPWRITE_PROJECT_ID)
    )
    
    if authenticated and settings.APPWRITE_API_KEY:
        client.set_key(settings.APPWRITE_API_KEY)
    
    return client

# Initialize default clients
client = make_client()
appwrite_account = Account(client)
appwrite_db = Databases(client)

async def create_task(appwrite_db, title: str) -> Task:
    """Create a new task with empty subtasks list"""
    task_id = uuid.uuid4().hex
    task_dict = {
        "id": task_id,
        "title": title,
        "completed": False,
        "completed_at": None,
        "notes": ""
    }
    await appwrite_db.create_document(
        settings.DATABASE_ID,
        "tasks",
        task_id,
        task_dict
    )
    task_dict["subtasks"] = []  # Initialize with empty subtasks
    return Task(**task_dict)

async def add_subtask(appwrite_db, parent_id: str, title: str) -> SubTask:
    """Add a subtask to existing task"""
    current_subtasks = await appwrite_db.get_document(
        settings.DATABASE_ID,
        "subtasks",
        queries=[Query.equal("parent_id", parent_id)]
    )
    
    # Calculate next order
    next_order = len(current_subtasks)
    
    subtask_id = uuid.uuid4().hex
    subtask_dict = {
        "id": subtask_id,
        "parent_id": parent_id,
        "title": title,
        "completed": False,
        "completed_at": None,
        "order": next_order
    }
    await appwrite_db.update_document(
        settings.DATABASE_ID,
        "subtasks",
        subtask_id,
        subtask_dict
    )
    return SubTask(**subtask_dict)

def get_subtasks(appwrite_db, parent_id: str) -> list[SubTask]:
    """Get all subtasks for a given parent task"""
    subtasks = appwrite_db.list_documents(
        settings.DATABASE_ID,
        "subtasks",
        queries=[Query.equal("parent_id", parent_id), Query.order_asc("order")]
    )
    # Convert to Subtask model
    subtasks = [
        SubTask(
            **{
                "id": subtask["$id"],  # Convert $id to id
                **{k: v for k, v in subtask.items() if k != "$id"}  # Include all other fields
            }
        ) for subtask in subtasks["documents"]
        ]
    return subtasks

def get_tasks(appwrite_db) -> list[Task]:
    """Get all tasks with their subtasks"""
    tasks = appwrite_db.list_documents(
        settings.DATABASE_ID,
        "tasks",
        )
    for task in tasks["documents"]:
        task["subtasks"] = get_subtasks(appwrite_db, task["$id"])
    # Convert to Task model
    tasks = [
        Task(
            **{
                "id": task["$id"],  # Convert $id to id
                "title": task.get("title", ""),
                "completed": task.get("completed", False),
                "completed_at": task.get("completed_at"),
                "notes": task.get("notes", ""),
                "subtasks": task.get("subtasks", []),  # Ensure subtasks are included
            }
        ) for task in tasks["documents"]
    ]
    return tasks

def get_task(appwrite_db, task_id: str) -> Task:
    """Get a specific task by ID with its subtasks"""
    task = appwrite_db.get_document(
        settings.DATABASE_ID,
        "tasks",
        queries=[Query.equal("$id", task_id)]
    )
    if not task:
        return None
    # Fetch subtasks
    task["subtasks"] = get_subtasks(appwrite_db, task_id)
    # Convert to Task model
    return Task(**task)

async def update_task_status(appwrite_db, user_id: str, task: Task, nested: bool = False) -> None:
    """Update task status by creating a checkin and updating task state"""
    # 1. Create checkin
    checkin = Checkin(
        user_id=user_id,
        task_id=task.id,
        completed=task.completed,
        note=task.notes,
        updated_at=datetime.now()
    )
    # Generate composite ID for checkin
    checkin.create_id()
    checkin = save_checkin(appwrite_db, checkin)
    
    # 2. Update task status 
    appwrite_db.update_document(
        settings.DATABASE_ID,
        "tasks",
        task.id,
        data={
            "completed": task.completed,
            "completed_at": task.completed_at,
            "notes": task.notes
        }
    )
    
    # 3. Update all subtasks
    if not nested:
        for subtask in task.subtasks:
            subtask.completed = task.completed
            subtask.completed_at = task.completed_at
            update_subtask_status(appwrite_db, subtask, nested=True) # nested update doesn't create a new checkin
    

async def update_subtask_status(appwrite_db, subtask: SubTask, nested: bool = False) -> None:
    """Update subtask status and create a checkin if not nested"""
    # 1. Create checkin
    if not nested:
        checkin = Checkin(
            user_id=subtask.user_id,
            task_id=subtask.parent_id,
            completed=subtask.completed,
            note=subtask.note,
            subtask_id=subtask.id,
            updated_at=datetime.now()
        )
        checkin.create_id()
        save_checkin(appwrite_db, checkin)
    
    # 2. Update subtask
    appwrite_db.update_document(
        settings.DATABASE_ID,
        "subtasks",
        subtask.id,
        data={
            "completed": subtask.completed,
            "completed_at": subtask.completed_at,
        }
    )

    # 3. If not nested, check parent task status and update parent task
    if not nested:
        task = get_task(appwrite_db, subtask.parent_id)
        if not task:
            raise ValueError(f"Parent task with ID {subtask.parent_id} not found")
        
        # Check if all subtasks complete and update task status
        if all(st.completed for st in task.subtasks):
            update_task_status(appwrite_db, task, nested=True) 

def get_user_checkins(appwrite_db, uid: str, date: str = None) -> list[Checkin]:
    """Get checkins for a specific user, defaulting to today if no date provided"""
    date = datetime.now().date().isoformat() if date is None else date
    q = [
        Query.equal("user_id", uid), 
        Query.equal("date", date)
    ]
    res = appwrite_db.list_documents(
        settings.DATABASE_ID, 
        "checkins",
        queries=q
    )
    return [Checkin(**doc) for doc in res["documents"]]

def get_task_checkins(appwrite_db, task_id: str, date: str = None) -> list[Checkin]:
    """Get checkins for a specific task, defaulting to today if no date provided"""
    date = datetime.now().date().isoformat() if date is None else date
    q = [
        Query.equal("task_id", task_id), 
        Query.equal("completed_at", date)
    ]
    res = appwrite_db.list_documents(
        settings.DATABASE_ID, 
        "checkins",
        queries=q
    )
    return [Checkin(**doc) for doc in res["documents"]]

def save_checkin(appwrite_db, checkin: Checkin) -> None:
    """Save checkin for task or subtask"""
    appwrite_db.create_document(
        settings.DATABASE_ID,
        "checkins",
        checkin.id,
        checkin.__dict__
        )