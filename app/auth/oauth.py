from fasthtml.common import *
import urllib.parse
from core.config import settings
from appwrite.services.account import Account
from core.appwrite_client import make_client

def google_oauth_url() -> str:
    """Build the Google OAuth2 redirect URL for Appwrite OAuth flow"""
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

async def verify_oauth_token(jwt_token: str) -> dict:
    """Verify OAuth JWT token and return user data"""
    if not jwt_token:
        raise ValueError("No JWT token provided")
        
    user_client = make_client(authenticated=False).set_jwt(jwt_token)
    user = Account(user_client).get()
    return {"id": user["$id"], "email": user["email"]}