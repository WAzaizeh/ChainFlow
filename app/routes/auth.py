from http import client
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
        # Clear any existing session on login page load
        NotStr(f"""
          <script>
            // Clear any existing session on login page load
            const {{ Client, Account }} = Appwrite;
            const client = new Client()
              .setEndpoint("{settings.APPWRITE_ENDPOINT}")
              .setProject("{settings.APPWRITE_PROJECT_ID}");
            const account = new Account(client);

            // Clear session silently
            account.deleteSession('current').catch(() => {{}});
          </script>
        """),
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

# @rt("/login/google", methods=["POST"])
# async def login_post(req, session, account: Account):
#     form = await req.form()
#     try:
#         sess = account.create_email_password_session(
#             email=form["email"],
#             password=form["password"]
#         )
#         session["user"] = {"id": sess["userId"], "email": form["email"]}
#         return RedirectResponse("/", status_code=303)
#     except Exception as e:
#         return Titled("Login failed", P(str(e)), A("Back", href="/login"))

# --- OAuth SUCCESS landing: grab JWT in browser & hand to backend ----------
@rt("/login/google")
def google_kickoff(req: Request):
    """Redirect to Google OAuth2 TOKEN flow."""
    # Get base URL
    host = req.headers.get("host", settings.APP_URL.replace("http://", "").replace("https://", ""))
    scheme = "http" if host.startswith("localhost") else (
        req.headers.get("x-forwarded-proto") or "https"
    )
    base_url = f"{scheme}://{host}"
    
    # Use server-side OAuth URL generation (not client-side createOAuth2Token)
    oauth_url = google_oauth_url(base_url)
    
    # Direct redirect to OAuth URL
    return RedirectResponse(url=oauth_url, status_code=303)

# --- OAuth2 Token Callback --------------------------------------------------
@rt("/oauth/google")
async def oauth_callback(req: Request, session):
    """Handle OAuth2 token callback - userId and secret come from URL params"""
    
    # Get userId and secret from URL parameters (these come from Appwrite OAuth callback)
    params = req.query_params
    user_id = params.get("userId")
    secret = params.get("secret")  # Changed back to "secret" - this is what Appwrite sends
    
    print("🔍 OAuth callback hit")
    print("Full URL:", str(req.url))
    print("Query params:", dict(req.query_params))
    print("userId:", user_id)
    print("secret:", secret[:20] + "..." if secret else None)

    if not user_id or not secret:
        print("⚠️ Missing userId or secret")
        return Div(
            H1("OAuth Debug"),
            P(f"Full URL: {req.url}"),
            P(f"Query params: {dict(req.query_params)}"),
            P(f"userId: {user_id}"),
            P(f"secret: {secret[:20] + '...' if secret else None}"),
        )

    # Handle client-side session creation and JWT generation
    return Titled(
        "Completing sign-in...",
        NotStr(f"""
          <script type="module">
            const {{ Client, Account }} = Appwrite;
            const client = new Appwrite.Client()
              .setEndpoint("{settings.APPWRITE_ENDPOINT}")
              .setProject("{settings.APPWRITE_PROJECT_ID}");
            const account = new Appwrite.Account(client);

            try {{
              console.log("Creating session from OAuth token...");
              console.log("userId:", "{user_id}");
              console.log("secret:", "{secret}".substring(0, 20) + "...");
              
              // Step 1: Create session using userId and secret from URL
              await account.createSession('{user_id}', '{secret}');
              console.log("✅ Session created successfully");
              
              // Step 2: Create JWT token for backend authentication
              const {{ jwt }} = await account.createJWT();
              console.log("✅ JWT created successfully");
              
              // Step 3: Send JWT to backend for FastHTML session storage
              const formData = new FormData();
              formData.append("jwt", jwt);
              
              const response = await fetch("/oauth-token", {{
                method: "POST",
                body: formData,
                credentials: "include"
              }});
              
              if (response.ok) {{
                console.log("✅ Backend authentication successful");
                window.location.href = "/";
              }} else {{
                throw new Error("Backend authentication failed");
              }}
              
            }} catch (error) {{
              console.error("❌ OAuth flow failed:", error);
              window.location.href = "/login?failed=1&error=" + encodeURIComponent(error.message);
            }}
          </script>
        """)
    )

@rt("/oauth-token", methods=["POST"])
async def oauth_token(req, session):
    form = await req.form()

    jwt = form.get("jwt")
    if not jwt:
        return RedirectResponse("/login?failed=1&error=Missing JWT", status_code=303)

    try:
        user_data = await verify_oauth_token(jwt)
        
        # Check if user is in allowed list
        ALLOWED_EMPLOYEES = [
            "wesam.azaizeh@gmail.com",  # Replace with actual allowed emails
            "another-employee@company.com"
        ]
        
        if user_data["email"] not in ALLOWED_EMPLOYEES:
            return RedirectResponse(
                "/login?failed=1&error=Access denied. Contact admin for access.",
                status_code=303
            )
        
        session["user"] = user_data
        print(f"✅ FastHTML session set for user: {user_data}")
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        print("❌ OAuth token error:", str(e))
        return RedirectResponse(
            f"/login?failed=1&error={urllib.parse.quote(str(e))}",
            status_code=303,
        )