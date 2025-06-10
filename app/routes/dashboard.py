from core.app import app, rt
from fasthtml.common import *
from core.appwrite_client import (
    get_database,
    get_tasks,
    get_task,
    save_checkin,
    get_subtask,
    update_subtask_status,
    update_task_status
)
from layout.tasks import tasks_container
from datetime import datetime
from models.checkins import Checkin
from layout.tasks import (
    task_checkbox,
    subtask_checkbox,
    task_note,
    subtask_container
)
import asyncio

@rt("/tasks")
def home(req):
    appwrite_db = get_database()
    user = req.scope["user"]
    tasks = get_tasks(appwrite_db)

    user_info = Div(cls="bg-white p-6 mb-6 rounded-lg shadow-sm")(
        H2("User Information", cls="text-xl font-semibold mb-4"),
        P(f"Email: {user['email']}", cls="text-gray-700"),
        P(f"User ID: {user['id']}", cls="text-gray-500 text-sm")
    )

    return Titled(
        "Today's Tasks",
        Div(cls="container mx-auto p-4 max-w-4xl")(
            user_info,
            H1("Today's Tasks", cls="text-2xl font-bold mb-6"),
            Ul(
                *[tasks_container(t) for t in tasks],
                cls="list-none p-0"
            )
        )
    )

@rt("/update")
async def update(req, session):
    appwrite_db = get_database()
    user = session.get("user")
    if not user:
        return Response(status_code=403)
    
    data = await req.form()
    task_id = data["task_id"]
    subtask_id = data.get("subtask_id")
    if "done" in data:
        completed = data.get("done") == "on"
        completed_at = datetime.now().isoformat()
    else:
        completed, completed_at = None, None
    notes = data.get("note", None)
    
    # Create checkin
    new_checkin = Checkin(
        user_id=user["id"],
        task_id=task_id,
        completed=completed,
        completed_at=completed_at,
        note=notes,
        subtask_id=subtask_id
    )
    save_checkin(appwrite_db, new_checkin)
    
    if subtask_id:
        # Handle subtask update
        subtask = get_subtask(appwrite_db, subtask_id)
        subtask.completed = completed
        subtask.completed_at = completed_at
        result = await update_subtask_status(appwrite_db, user["id"], subtask)
        if result["task_updated"]:
            return Div(
                subtask_container(result["subtask"]),
                Div(task_checkbox(result["task"]), hx_swap_oob="true")
            )
        return subtask_container(result["subtask"])
        
    else:
        # Handle task update
        task = get_task(appwrite_db, task_id)
        task.completed = completed 
        task.completed_at = completed_at
        task.notes = notes
        result = await update_task_status(appwrite_db, user["id"], task)
        subtasks_html = [subtask_container(st) for st in result["updated_subtasks"]]
        return Div(
            task_checkbox(result["task"]),
            *[Div(st, hx_swap_oob="true") for st in subtasks_html]
        )
    
@rt("/tasks/{task_id}/toggle")
async def toggle_task(req, session, task_id: str):
    """Handle task completion toggle with optimistic updates"""
    appwrite_db = get_database()
    task = get_task(appwrite_db, task_id)
    task.completed = not task.completed
    task.completed_at = datetime.now().isoformat()

    # Create checkin
    checkin = Checkin(
        user_id=session["user"]["id"],
        task_id=task.id,
        completed=task.completed,
        completed_at=task.completed_at,
        note=task.notes
    )
    save_checkin(appwrite_db, checkin)

    # Update the task in the database
    await update_task_status(appwrite_db, session["user"]["id"], task)
    
    # Prepare all updates in parallel
    subtask_updates = []
    for subtask in task.subtasks:
        if subtask.completed != task.completed:
            subtask.completed = task.completed
            subtask.completed_at = task.completed_at
            subtask_updates.append(
                update_subtask_status(appwrite_db, session["user"]["id"], subtask, nested=True)
            )
    
    # Update subtasks in parallel if any
    if subtask_updates:
        await asyncio.gather(*subtask_updates)
    
    # Return minimal update
    return tasks_container(task)

@rt("/tasks/subtask/{subtask_id}/toggle")
async def toggle_subtask(req, session, subtask_id: str):
    """Handle subtask completion toggle"""
    appwrite_db = get_database()
    subtask = get_subtask(appwrite_db, subtask_id)
    subtask.completed = not subtask.completed
    result = await update_subtask_status(appwrite_db, session["user"]["id"], subtask)
    return subtask_checkbox(result["subtask"])

@rt("/tasks/{task_id}/note")
async def update_note(req, session, task_id: str):
    appwrite_db = get_database()
    """Handle task note update"""
    data = await req.form()
    task = get_task(appwrite_db, task_id)
    task.notes = data.get("note", "")
    await update_task_status(appwrite_db, session["user"]["id"], task)
    return task_note(task)