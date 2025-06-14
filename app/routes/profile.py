from core.app import rt
from fasthtml.common import *
from layout.pages import ProfilePage
from datetime import datetime

@rt('/profile')
async def profile(session):
    """User profile page"""
    user = {"id": session["user"]["id"], "email": session["user"]["email"]}
    return ProfilePage(user)