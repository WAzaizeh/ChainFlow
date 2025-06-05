from core.app import app, rt
from fasthtml.common import *
from core.appwrite_client import (
    appwrite_db,
    get_tasks,
    get_task_checkins,
    save_checkin
)
from layout.tasks import tasks_container

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
    save_checkin(appwrite_db, uid=user["id"], tid=data["task_id"], done=data.get("done") == "on", note=data.get("note", ""))
    return Response(status_code=204)