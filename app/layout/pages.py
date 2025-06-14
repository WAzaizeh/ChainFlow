from fasthtml.common import *
from components.page import AppContainer
from components.navigation import BottomNav
from models.task import Task
from .tasks import tasks_container
from models.inventory import InventoryItem
from layout.inventory import (
    inventory_edit_view,
    inventory_table_view,
    inventory_add_item
)

def TasksPage(tasks: list[Task]) -> AppContainer:
    """Tasks page layout with container and navigation"""
    return AppContainer(
        Div(cls="container mx-auto p-4 max-w-4xl")(
            H1("Tasks", cls="text-2xl font-bold mb-6"),
            Ul(
                *[tasks_container(task) for task in tasks],
                cls="list-none p-0"
            )
        ),
        BottomNav(active_button_index=1)  # Assuming tasks is the second nav item
    )

def InventoryPage(items: list[InventoryItem]) -> Div:
    """Main inventory page with tabs"""
    return AppContainer( 
        Div(cls="container mx-auto p-4 max-w-4xl")(
        # Success message
        Div(
            id="success-message",
            cls="fixed top-4 left-1/2 transform -translate-x-1/2 bg-green-500 \
                text-white px-6 py-3 rounded-lg shadow-lg opacity-0 transition-opacity \
                duration-200 z-50",
            style="pointer-events: none"
        )("Inventory Updated Successfully"),
        
        # Tab Container using DaisyUI v4 radio tabs
        Div(cls="flex flex-col gap-2")(
            # Tabs
            Div(
                role="tablist",
                id="inventory-tabs",
                cls="tabs tabs-lifted"
                )(
                Input(
                    type="radio",
                    name="inventory_tab",
                    role="tab",
                    cls="tab",
                    id="edit-tab",
                    checked=True,
                    aria_label="Edit"
                ),
                Div(
                    role="tabpanel",
                    cls="tab-content bg-base-100 border-base-300 rounded-box p-6",
                    id="edit-content",
                    *inventory_edit_view()
                ),
                Input(
                    type="radio",
                    name="inventory_tab",
                    role="tab",
                    cls="tab",
                    id="view-tab",
                    aria_label="View"
                ),
                Div(
                    role="tabpanel",
                    cls="tab-content bg-base-100 border-base-300 rounded-box p-6",
                    id="view-content",
                    *inventory_table_view(items)
                ),
                Input(
                    type="radio",
                    name="inventory_tab",
                    role="tab",
                    cls="tab",
                    id="add-tab",
                    aria_label="Add New"
                ),
                Div(
                    role="tabpanel",
                    cls="tab-content bg-base-100 border-base-300 rounded-box p-6",
                    id="add-content",
                    *inventory_add_item()
                ),
            )
        )
    ),
    BottomNav(active_button_index=2)  # Assuming inventory is the third nav item
    )

def ProfilePage(user) -> AppContainer:
    """Profile page placeholder"""
    return AppContainer(
        Div(cls="container mx-auto p-4 max-w-4xl")(
            H1("Profile", cls="text-2xl font-bold mb-6"),
            P(f"Email: {user['email']}", cls="text-gray-700"),
            P(f"User ID: {user['id']}", cls="text-gray-700")
        ),
        BottomNav(active_button_index=3)  # Assuming profile is the fourth nav item
    )