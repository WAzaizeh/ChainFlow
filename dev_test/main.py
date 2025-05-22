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
import os, datetime, json
from dotenv import load_dotenv
import urllib.parse
from appwrite.query import Query

# ---------------------------------------------------------------------------
# ENV & helpers
# ---------------------------------------------------------------------------
load_dotenv()
ENDPOINT   = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "YOUR_PROJECT_ID")
APP_URL    = os.getenv("APP_URL", "http://localhost:5001")


def make_client(authenticated=True):
    """
    Creates an Appwrite client instance.
    
    Args:
        authenticated (bool): If True, includes API key for authenticated server operations.
                            If False, creates an unauthenticated client for public/user operations.
    
    Returns:
        Client: Configured Appwrite client instance
    """
    client = (
        Client()
        .set_endpoint(ENDPOINT)
        .set_project(PROJECT_ID)
    )
    
    if authenticated:
        api_key = os.getenv("APPWRITE_API_KEY", "")
        if api_key:
            client.set_key(api_key)
    
    return client

client  = make_client()
account = Account(client)
db      = Databases(client)

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
login_redir = RedirectResponse("/login", status_code=303)


def auth_before(req, sess):
    user = sess.get("user")
    if not user:
        return login_redir
    req.scope["user"] = user

beforeware = Beforeware(
    auth_before,
    skip=[r"/login.*", r"/static/.*", r"/favicon.*", r"/assets/.*", r"/oauth.*", r"/login/google", r"/oauth-token"],
)

# ---------------------------------------------------------------------------
# FastHTML app
# ---------------------------------------------------------------------------
hdrs = (Meta(name="viewport", content="width=device-width, initial-scale=1.0"),)
app, rt = fast_app(before=beforeware, hdrs=hdrs)

# ---------------------------------------------------------------------------
# DB wrappers
# ---------------------------------------------------------------------------
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")
TASKS_COLLECTION_ID = os.getenv("APPWRITE_TASKS_COLLECTION_ID")
CHECKINS_COLLECTION_ID = os.getenv("APPWRITE_CHECKINS_COLLECTION_ID")

def get_tasks():
    return db.list_documents(DATABASE_ID, TASKS_COLLECTION_ID)["documents"]


def get_today_checkins(uid: str):
    today = datetime.date.today().isoformat()
    q=[Query.equal("user_id", uid), Query.equal("date", today)]
    res = db.list_documents(DATABASE_ID, CHECKINS_COLLECTION_ID, queries=q)
    return {d["task_id"]: d for d in res["documents"]}


def save_checkin(uid: str, tid: str, done: bool, note: str):
    today = datetime.date.today().isoformat()
    q = [Query.equal("user_id", uid), Query.equal("task_id", tid), Query.equal("date", today)]
    found = db.list_documents(DATABASE_ID, CHECKINS_COLLECTION_ID, queries=q)
    data = dict(task_id=tid, user_id=uid, date=today, done=done, note=note)
    if found["total"]:
        db.update_document(DATABASE_ID, CHECKINS_COLLECTION_ID, found["documents"][0]["$id"], data=data)
    else:
        db.create_document(DATABASE_ID, CHECKINS_COLLECTION_ID, ID.unique(), data=data)

# ---------------------------------------------------------------------------
# Google OAuth URLs
# ---------------------------------------------------------------------------

def google_oauth_url() -> str:
    """
    Build the Google OAuth2 redirect URL exactly the way Appwrite’s
    client SDK does: one scopes[]= entry per scope.
    """
    success = urllib.parse.quote(f"{APP_URL}/oauth/google", safe="")
    failure = urllib.parse.quote(f"{APP_URL}/login?failed=1", safe="")

    scopes = ["openid", "email"]
    scope_params = "&".join(
        f"scopes[]={urllib.parse.quote(s, safe='')}" for s in scopes
    )

    return (
        f"{ENDPOINT}/account/sessions/oauth2/google"
        f"?project={PROJECT_ID}"
        f"&success={success}"
        f"&failure={failure}"
        f"&{scope_params}"
    )

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@rt("/login")
def login_get(req):
    failed = req.query_params.get("failed")
    err = P("Google sign‑in failed, try again.", cls="text-red-600") if failed else ""
    return Titled(
        "Sign in",
        err,
        Form(method="post", cls="container flex flex-col gap-3")(
            Fieldset(
                Label("Email",  Input(name="email", type="email", required=True)),
                Label("Password",Input(name="password", type="password", required=True)),
            ),
            Button("Login", type="submit"),
        ),
        Hr(),
        A("Continue with Google", href="/login/google", cls="btn btn-outline w-full"),
    )


@rt("/login")
async def login_post(req, session):                 # <- async
    form = await req.form()                         # <- await
    try:
        sess = account.create_email_password_session(
            email=form["email"],
            password=form["password"]
        )
        session["user"] = {"id": sess["userId"], "email": form["email"]}
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        return Titled("Login failed", P(str(e)), A("Back", href="/login"))


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
              .setEndpoint("{ENDPOINT}")
              .setProject("{PROJECT_ID}");
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
