from core.app import app, rt
from fasthtml.common import *
from core.appwrite_client import (
    make_client,
    get_tasks,
    get_today_checkins,
    save_checkin
)
import json

@rt("/")
def home(req):
    user   = req.scope["user"]
    tasks  = get_tasks()
    checks = get_today_checkins(user["id"])

    # Add user info section at the top
    user_info = Div(cls="bg-gray-100 p-4 mb-6 rounded shadow")(
        H2("User Information", cls="text-xl mb-2"),
        P(f"Email: {user['email']}", cls="text-gray-700"),
        P(f"User ID: {user['id']}", cls="text-gray-700"),
        Hr(cls="my-4")
    )

    def row(t):
        chk = checks.get(t["$id"], {})
        task_name = t.get("name", "")
        if isinstance(task_name, str):
            task_name = json.loads(task_name)["name"]
        return Li(cls="flex items-center gap-2 py-2")(
            Input(type="checkbox", name="done", checked=chk.get("done", False),
                  hx_post="/update", hx_include="closest li", cls="mr-2"),
            Span(task_name, cls="flex-1"),
            Input(type="text", name="note", value=chk.get("note", ""), placeholder="Note…",
                  hx_post="/update", hx_include="closest li", cls="flex-1"),
            Input(type="hidden", name="task_id", value=t["$id"]),
        )

    return Titled(
        "Today's Tasks",
        Div(cls="container mx-auto p-4")(
            user_info,
            H1("Today's Tasks", cls="text-2xl mb-4"),
            Ul(*[row(t) for t in tasks], cls="list-none p-0")
        )
    )

@rt("/update")
async def update(req, session):
    user = session.get("user")
    if not user:
        return Response(status_code=403)
    data = await req.form()
    save_checkin(uid=user["id"], tid=data["task_id"], done=data.get("done") == "on", note=data.get("note", ""))
    return Response(status_code=204)