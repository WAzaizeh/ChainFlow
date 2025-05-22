"""
FastHTML + Appwrite task tracker
--------------------------------
Now with Google OAuth!

Running locally:
  APP_URL=http://localhost:5001  (default)
  APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
  APPWRITE_PROJECT_ID=xxxxx
  # optional: APPWRITE_API_KEY=... (for server‑side privileged ops)

The flow:
1.   `/login` shows email/password form **and** a *Continue with Google* button.
2.   Button hits `/login/google` which redirects to Appwrite's hosted OAuth screen.
3.   Appwrite sends the browser back to `/oauth/google` (success URL).
4.   That page runs a tiny JS snippet:
       – `account.createJWT()` (because the browser is now logged‑in on *.cloud.appwrite.io*)
       – POSTs that JWT to `/oauth-token`.
5.   Backend validates JWT → fetches user profile → stores `{id,email}` in FastHTML session.
6.   User is now authenticated like a normal email/password user.

Note: Because Appwrite Cloud lives on a different origin, we hop through `createJWT()` → backend so the server can act on behalf of the user (write check‑ins, etc.).
"""

from fasthtml.common import *
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.id import ID
import datetime, json
import urllib.parse
from appwrite.query import Query
from core.app import app, rt
import routes
from core.config import settings
from core.appwrite_client import (
    make_client,
    account,
    get_tasks,
    get_today_checkins,
    save_checkin
)
# ---------------------------------------------------------------------------
# Google OAuth URLs
# ---------------------------------------------------------------------------

def google_oauth_url() -> str:
    """
    Build the Google OAuth2 redirect URL exactly the way Appwrite’s
    client SDK does: one scopes[]= entry per scope.
    """
    success = urllib.parse.quote(settings.oauth_success_url, safe="")
    failure = urllib.parse.quote(settings.oauth_failure_url, safe="")

    scope_params = "&".join(
        f"scopes[]={urllib.parse.quote(s, safe='')}" 
        for s in settings.OAUTH_SCOPES
    )

    return (
        f"{settings.APPWRITE_ENDPOINT}/account/sessions/oauth2/google"
        f"?project={settings.APPWRITE_PROJECT_ID}"
        f"&success={success}"
        f"&failure={failure}"
        f"&{scope_params}"
    )

# ---------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

# --- Google OAuth kickoff ---------------------------------------------------
@rt("/login/google")
def google_kickoff():
    return RedirectResponse(google_oauth_url(), status_code=302)

# --- OAuth SUCCESS landing: grab JWT in browser & hand to backend ----------
@rt("/oauth/google")
def google_success(req):
    """
    We *always* return a tiny HTML page that finishes auth in JS.
    Server-side never sees the cookie or fragment.
    """
    return Titled(
        "Finishing sign-in…",
        NotStr(f"""
          <script type="module">
            import * as Appwrite from "https://cdn.jsdelivr.net/npm/appwrite@13.0.0/+esm";
            const client  = new Appwrite.Client()
              .setEndpoint("{settings.APPWRITE_ENDPOINT}")
              .setProject("{settings.APPWRITE_PROJECT_ID}");
            const account = new Appwrite.Account(client);

            try {{
              const {{ jwt }} = await account.createJWT();   // 15-min user token
              const formData = new FormData();
              formData.append("jwt", jwt);
              await fetch("/oauth-token", {{
                method: "POST",
                body:   formData,
                credentials: "include"
              }});
              window.location.href = "/";
            }} catch (err) {{
              console.error(err);
              window.location.href = "/login?failed=1&error=" + encodeURIComponent(err.message);
            }}
          </script>
        """)
    )
    
# --- Backend receives JWT, verifies, starts session ------------------------
@rt("/oauth-token")
async def oauth_token(req, session):                # <- async
    form = await req.form()                         # <- await

    jwt = form.get("jwt")
    if not jwt:
        return RedirectResponse("/login?failed=1", status_code=303)

    try:
        user_client = make_client(authenticated=False).set_jwt(jwt)
        user        = Account(user_client).get()
        session["user"] = {"id": user["$id"], "email": user["email"]}
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        return RedirectResponse(
            f"/login?failed=1&error={urllib.parse.quote(str(e))}",
            status_code=303,
        )

# ---------- Dashboard -------------------------------------------------------
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

# ---------- HTMX update -----------------------------------------------------
@rt("/update")
async def update(req, session):
    user = session.get("user")
    if not user:
        return Response(status_code=403)
    data = await req.form()
    save_checkin(uid=user["id"], tid=data["task_id"], done=data.get("done") == "on", note=data.get("note", ""))
    return Response(status_code=204)

# ---------------------------------------------------------------------------
serve()
