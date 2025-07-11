from fasthtml.common import *
from core.appwrite_client import create_client, get_account
from auth.oauth import google_oauth_url
from core.config import settings
import urllib.parse
from appwrite.services.account import Account
from core.app import rt
from auth.oauth import verify_oauth_token


@rt("/login", methods=["GET"])
def login_get(req):
    failed = req.query_params.get("failed")
    error_msg = req.query_params.get("error", "n")
    state = req.query_params.get("state", "m")
    code = req.query_params.get("code", "s")

    err = (
        Div(cls="text-red-600 space-y-2")(
            P("Google sign‑in failed, try again."),
            Div(cls="text-sm font-mono bg-red-50 p-2 rounded space-y-1")(
                P(f"Error: {error_msg}"),
                P(f"State: {state}"),
                P(f"Code: {code}")
            )
        ) if failed else ""
    )
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
def google_kickoff(req):
    """Redirect to Google OAuth2 login"""
    # Get the host from the request
    request_host = req.headers.get('host', settings.APP_URL.replace('http://', '').replace('https://', ''))
    
    # Determine protocol based on host or headers
    if (request_host.startswith('localhost') or 
        request_host.startswith('127.0.0.1') or 
        request_host.startswith('0.0.0.0')):
        protocol = 'http'
    else:
        # Check for forwarded protocol headers (common in reverse proxies)
        protocol = (req.headers.get('x-forwarded-proto') or 
                   req.headers.get('x-forwarded-protocol') or 
                   'https')
    
    base_url = f"{protocol}://{request_host}"
    oauth_url = google_oauth_url(base_url)

    return RedirectResponse(
        oauth_url,
        status_code=303
    )

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
              console.log("Creating JWT...");
              const {{ jwt }} = await account.createJWT();
              console.log("JWT created successfully");
              const formData = new FormData();
              formData.append("jwt", jwt);
              await fetch("/oauth-token", {{
                method: "POST",
                body:   formData,
                credentials: "include"
              }});
              window.location.href = "/";
            }} catch (err) {{
              console.error("JWT creation failed:", err);
              window.location.href = "/login?failed=1&error=" + encodeURIComponent(err.message);
            }}
          </script>
        """)
    )

@rt("/oauth-token", methods=["POST"])
async def oauth_token(req, session):
    form = await req.form()

    jwt = form.get("jwt")
    if not jwt:
        return RedirectResponse("/login?failed=1", status_code=303)
        

    try:
        user_data = await verify_oauth_token(jwt)
        session["user"] = user_data
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        return RedirectResponse(
            f"/login?failed=1&error={urllib.parse.quote(str(e))}",
            status_code=303,
        )