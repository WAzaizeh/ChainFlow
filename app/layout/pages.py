from fasthtml.common import *
from components.page import AppContainer
from components.navigation import BottomNav
from models.task import Task
from .tasks import tasks_container

def TasksPage(tasks: list[Task]):
    """Tasks page layout with container and navigation"""
    return AppContainer(
        Div(cls="container mx-auto p-4 max-w-4xl")(
            H1("Tasks", cls="text-2xl font-bold mb-6"),
            Ul(
                *[tasks_container(task) for task in tasks],
                cls="list-none p-0"
            )
        ),
        BottomNav(active_button_index=2)  # Assuming tasks is the third nav item
    )