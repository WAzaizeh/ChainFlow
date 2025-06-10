from fasthtml.common import *
from core.appwrite_client import create_client, get_account
from auth.oauth import google_oauth_url
from core.config import settings
import urllib.parse
from appwrite.services.account import Account
from core.app import rt

@rt("/login", methods=["GET"])
def login_get(req):
    failed = req.query_params.get("failed")
    err = P("Google sign‑in failed, try again.", cls="text-red-600") if failed else ""
    return Titled(
        "Sign in",
        err,
        Form(method="post", cls="container flex flex-col gap-3")(
            Fieldset(
                Label("Email", Input(name="email", type="email", required=True)),
                Label("Password", Input(name="password", type="password", required=True)),
            ),
            Button("Login", type="submit"),
        ),
        Hr(),
        A("Continue with Google", href="/login/google", cls="btn btn-outline w-full"),
    )

@rt("/login/google", methods=["POST"])
async def login_post(req, session, account: Account):
    form = await req.form()
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

@rt("/oauth-token")
async def oauth_token(req, session):
    form = await req.form()

    jwt = form.get("jwt")
    if not jwt:
        return RedirectResponse("/login?failed=1", status_code=303)

    try:
        user_client = create_client(authenticated=False).set_jwt(jwt)
        appwrite_account = get_account(user_client)
        user = appwrite_account(user_client).get()
        session["user"] = {"id": user["$id"], "email": user["email"]}
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        return RedirectResponse(
            f"/login?failed=1&error={urllib.parse.quote(str(e))}",
            status_code=303,
        )