from core.app import app, rt
from fasthtml.common import *
from core.appwrite_client import (
    appwrite_db,
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
from layout.tasks import subtask_container, task_checkbox

@rt("/")
def home(req):
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
    user = session.get("user")
    if not user:
        return Response(status_code=403)
    
    data = await req.form()
    task_id = data["task_id"]
    subtask_id = data.get("subtask_id")
    print(f"#########\n{data=}\n############")
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