from fasthtml.common import *
from urllib import parse
from core.config import settings
from appwrite.services.account import Account
from core.appwrite_client import create_client

def google_oauth_url(base_url: str) -> str:
    """Build the Google OAuth2 TOKEN redirect URL"""
    base_url = base_url.rstrip('/')
    
    success = f"{base_url}/oauth/google"
    failure = f"{base_url}/login"
    
    scope_params = "&".join(
        f"scopes[]={parse.quote(s, safe='')}" 
        for s in settings.OAUTH_SCOPES
    )

    # Use TOKEN endpoint (not session endpoint)
    oauth_url = (
        f"{settings.APPWRITE_ENDPOINT}/account/tokens/oauth2/google"  # tokens, not sessions
        f"?project={settings.APPWRITE_PROJECT_ID}"
        f"&success={parse.quote(success, safe='')}"
        f"&failure={parse.quote(failure, safe='')}"
        f"&{scope_params}"
    )
    
    return oauth_url

async def verify_oauth_token(jwt_token: str) -> dict:
    """Verify OAuth JWT token and return user data"""
    if not jwt_token:
        raise ValueError("No JWT token provided")
        
    user_client = create_client(authenticated=False).set_jwt(jwt_token)
    user = Account(user_client).get()
    return {"id": user["$id"], "email": user["email"]}