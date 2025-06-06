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
            id = subtask["$id"],  # Convert $id to id
            parent_id = subtask["parent_id"],
            title = subtask.get("title", ""),
            completed = subtask.get("completed", False),
            completed_at = subtask.get("completed_at"),
            order = subtask.get("order", 0)
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
        task_id
    )
    if not task:
        return None
    # Fetch subtasks
    task["subtasks"] = get_subtasks(appwrite_db, task_id)
    # Convert to Task model
    return Task(
        id=task["$id"],  # Convert $id to id
        title=task.get("title", ""),
        completed=task.get("completed", False),
        completed_at=task.get("completed_at"),
        notes=task.get("notes", ""),
        subtasks=task.get("subtasks", [])
        )

def get_subtask(appwrite_db, subtask_id: str) -> SubTask:
    """Get a specific subtask by ID"""
    subtask = appwrite_db.get_document(
        settings.DATABASE_ID,
        "subtasks",
        subtask_id
    )
    if not subtask:
        return None
    # Convert to SubTask model
    return SubTask(
        id = subtask["$id"],  # Convert $id to id
        parent_id = subtask["parent_id"],
        title = subtask.get("title", ""),
        completed = subtask.get("completed", False),
        completed_at = subtask.get("completed_at"),
        order = subtask.get("order", 0)
    )

async def update_task_status(appwrite_db, user_id: str, task: Task, nested: bool = False) -> None:
    """Update task status by creating a checkin and updating task state"""
    # 1. Create checkin, even if nested
    checkin = Checkin(
        user_id=user_id,
        task_id=task.id,
        completed=task.completed,
        note=task.notes,
        completed_at=datetime.now()
    )
    save_checkin(appwrite_db, checkin)
    
    # 2. Update task
    changes = {}
    if task.complete:
        changes["completed"] = task.completed
        changes["completed_at"] = task.completed_at
    elif task.notes:
        changes["notes"] = task.notes
    appwrite_db.update_document(
        settings.DATABASE_ID,
        "tasks",
        task.id,
        data=changes
    )
    
    # 3. Update subtasks if needed
    updated_subtasks = []
    if not nested:
        for subtask in task.subtasks:
            if subtask.completed != task.completed:
                subtask.completed = task.completed
                subtask.completed_at = task.completed_at
                await update_subtask_status(appwrite_db, user_id, subtask, nested=True) # nested update doesn't create a new checkin
                updated_subtasks.append(subtask)
    
    return {
        "task": task,
        "updated_subtasks": updated_subtasks
    }

async def update_subtask_status(appwrite_db, user_id: str, subtask: SubTask, nested: bool = False) -> None:
    """Update subtask status and create a checkin if not nested"""
    print(f"############\n{subtask=}\n############")
    # 1. Create checkin
    if not nested:
        checkin = Checkin(
            user_id=user_id,
            task_id=subtask.parent_id,
            completed=subtask.completed,
            completed_at=subtask.completed_at,
            subtask_id=subtask.id,
        )
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

    # 3. Check if parent task needs update
    if not nested:
        task = get_task(appwrite_db, subtask.parent_id)
        if not task:
            raise ValueError(f"Parent task with ID {subtask.parent_id} not found")
        
        # Check if all subtasks complete and update task status
        if all(st.completed for st in task.subtasks):
            task.completed = subtask.completed
            task.completed_at = subtask.completed_at
            await update_task_status(appwrite_db, user_id, task, nested=True)
            return {
                "subtask": subtask,
                "task_updated": True,
                "task": task
            }
    
    # If not all subtasks complete, just return the subtask
    return {
        "subtask": subtask,
        "task_updated": False
    }

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
    checkin.completed_at = checkin.completed_at.isoformat() if isinstance(checkin.completed_at, datetime) else checkin.completed_at
    checkin_dict = {k: v for k, v in checkin.__dict__.items() if k != 'id'}
    
    saved_checkin = appwrite_db.create_document(
        settings.DATABASE_ID,
        "checkins",
        ID.unique(),
        checkin_dict
    )
    
    return Checkin(
            id = saved_checkin["$id"],
            user_id = saved_checkin["user_id"],
            task_id = saved_checkin["task_id"],
            completed = saved_checkin["completed"],
            note = saved_checkin.get("note", ""),
            subtask_id = saved_checkin.get("subtask_id", None),
            completed_at = datetime.fromisoformat(saved_checkin["completed_at"]) if saved_checkin.get("completed_at") else None
        )
