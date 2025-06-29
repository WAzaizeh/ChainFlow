from fasthtml.common import *
import urllib.parse
from core.config import settings
from appwrite.services.account import Account
from core.appwrite_client import create_client

def google_oauth_url(base_url: str) -> str:
    """Build the Google OAuth2 redirect URL for Appwrite OAuth flow"""
    # Strip any trailing slashes
    base_url = base_url.rstrip('/')
    
    # Encode URLs with proper escaping
    success = urllib.parse.quote(f"{base_url}/oauth/google", safe="")
    failure = urllib.parse.quote(f"{base_url}/login", safe="")

    # Add debug logging
    print(f"OAuth redirect URLs: success={success}, failure={failure}")

    scope_params = "&".join(
        f"scopes[]={urllib.parse.quote(s, safe='')}" 
        for s in settings.OAUTH_SCOPES
    )

    oauth_url = (
        f"{settings.APPWRITE_ENDPOINT}/account/sessions/oauth2/google"
        f"?project={settings.APPWRITE_PROJECT_ID}"
        f"&success={success}"
        f"&failure={failure}"
        f"&{scope_params}"
    )

    # Add debug logging
    print(f"Final OAuth URL: {oauth_url}")
    return oauth_url

async def verify_oauth_token(jwt_token: str) -> dict:
    """Verify OAuth JWT token and return user data"""
    if not jwt_token:
        raise ValueError("No JWT token provided")
        
    user_client = create_client(authenticated=False).set_jwt(jwt_token)
    user = Account(user_client).get()
    return {"id": user["$id"], "email": user["email"]}