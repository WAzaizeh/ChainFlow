from fasthtml.common import *
from core.config import settings
import urllib.parse
from core.appwrite_client import make_client, appwrite_account

def google_oauth_url() -> str:
    """Build the Google OAuth2 redirect URL"""
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

async def handle_oauth_callback(jwt_token: str) -> dict:
    """Handle OAuth callback and return user data"""
    if not jwt_token:
        raise ValueError("No JWT token provided")
        
    user_client = make_client(authenticated=False).set_jwt(jwt_token)
    user = appwrite_account(user_client).get()
    return {"id": user["$id"], "email": user["email"]}