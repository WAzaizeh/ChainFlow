from core.app import app, rt
from fasthtml.common import *
from components.page import AppContainer
from components.navigation import BottomNav

@rt('/')
def home():
    """Home page with main action buttons"""
    return AppContainer(
        Div(cls="container mx-auto p-4 max-w-4xl")(
            H1("Dera Manager", cls="text-2xl font-bold mb-6 text-center"),
            # Main action buttons
            Div(cls="space-y-4")(
                A(
                    href="/inventory",
                    cls="w-full p-6 bg-white rounded-lg shadow-sm flex items-center \
                        justify-center text-lg font-medium hover:bg-gray-50 \
                        transition-colors duration-150"
                )("Edit Inventory"),
                A(
                    href="/tasks",
                    cls="w-full p-6 bg-white rounded-lg shadow-sm flex items-center \
                        justify-center text-lg font-medium hover:bg-gray-50 \
                        transition-colors duration-150"
                )("Closing Tasks")
            )
        ),
        # Bottom navigation
        BottomNav( active_button_index=0 )
    )