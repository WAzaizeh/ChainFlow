from core.app import rt
from fasthtml.common import *
from components.page import AppContainer
from components.navigation import BottomNav
from db.auth import AuthDatabase
from layout.navigation import render_main_navigation

@rt('/')
def home(session):
    """Home page with role-based navigation"""
    if not session.get('user'):
        return RedirectResponse('/login', status_code=303)
        
    auth_db = AuthDatabase()
    user_id = session['user']['id']
    user_role = auth_db.get_user_role(user_id)
    
    return AppContainer(
        Div(cls="container mx-auto p-4 max-w-4xl")(
            H1("Dera Manager", cls="text-2xl font-bold mb-6 text-center"),
            render_main_navigation(user_role)
        ),
        active_button_index= 1, # Assuming the first button is "Home"
    )