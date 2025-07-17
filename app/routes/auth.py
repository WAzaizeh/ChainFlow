from http import client
from fasthtml.common import *
from core.appwrite_client import create_client, get_account
from auth.oauth import google_oauth_url
from core.config import settings
import urllib.parse
from appwrite.services.account import Account
from core.app import rt
from auth.oauth import verify_oauth_token
import logging

logger = logging.getLogger(__name__)

@rt("/login", methods=["GET"])
def login_get(req):
    failed = req.query_params.get("failed")
    error_msg = req.query_params.get("error")
    state = req.query_params.get("state")
    code = req.query_params.get("code")

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

# --- OAuth SUCCESS landing: grab JWT in browser & hand to backend ----------
@rt("/login/google")
def google_kickoff(req: Request):
    """Redirect to Google OAuth2 TOKEN flow."""
    # Get base URL
    host = req.headers.get("host", settings.APP_URL.replace("http://", "").replace("https://", ""))
    # Handle localhost and production URLs
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

    if not user_id or not secret:
        logger.error(f"OAuth callback missing required parameters. URL: {req.url}, Params: {dict(req.query_params)}")

        error_msg = "OAuth callback missing required parameters"
        return RedirectResponse(
            f"/login?failed=1&error={urllib.parse.quote(error_msg)}", 
            status_code=303
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
              // Step 1: Create session using userId and secret
              await account.createSession('{user_id}', '{secret}');
              
              // Step 2: Create JWT token for backend authentication
              const {{ jwt }} = await account.createJWT();
              
              // Step 3: Send JWT to backend for FastHTML session storage
              const formData = new FormData();
              formData.append("jwt", jwt);
              
              const response = await fetch("/oauth-token", {{
                method: "POST",
                body: formData,
                credentials: "include"
              }});
              
              if (response.ok) {{
                window.location.href = "/";
              }} else {{
                throw new Error("Backend authentication failed");
              }}
              
            }} catch (error) {{
              console.error("OAuth flow failed:", error);
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
        logger.error("OAuth token endpoint called without JWT")
        return RedirectResponse("/login?failed=1&error=Missing JWT", status_code=303)

    try:
        logger.info("Verifying OAuth JWT token")
        user_data = await verify_oauth_token(jwt)
        
        # Check if user is in allowed list
        ALLOWED_EMPLOYEES = [
            "wesam.azaizeh@gmail.com",
            "mugalli789@gmail.com"
        ]
        
        user_email = user_data.get("email")
        logger.debug(f"🔧 Debug: Checking access for email: {user_email}")
        logger.debug(f"🔧 Debug: Allowed employees: {ALLOWED_EMPLOYEES}")
        
        if user_email not in ALLOWED_EMPLOYEES:
            logger.warning(f"🚫 Access denied for user: {user_email}")
            logger.debug(f"🔧 Debug: Email '{user_email}' not in allowed list")
            
            return RedirectResponse(
                "/login?failed=1&error=Access denied. Contact admin for access.",
                status_code=303
            )
        
        # Store user data in session
        session["user"] = user_data
        logger.info(f"✅ FastHTML session set for user: {user_email}")
        logger.debug(f"🔧 Debug: Session data keys: {list(session.keys())}")
                
        return RedirectResponse("/", status_code=303)
    
    except Exception as e:
        logger.error(f"OAuth token verification failed: {str(e)}")
        return RedirectResponse(
            f"/login?failed=1&error={urllib.parse.quote(str(e))}",
            status_code=303,
        )