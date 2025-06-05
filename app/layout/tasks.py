from fasthtml.common import *
from typing import Dict, Any
from models.task import Task, SubTask
import json

def subtask_container(subtask: SubTask) -> Li:
    """Render a subtask row with its checkbox"""
    
    return Li(
        id=f"subtask-{subtask.id}",
        cls="ml-8 flex items-center gap-2 py-1 border-l-2 border-gray-200 pl-4")(
        Input(
            type="checkbox",
            name="done",
            checked=subtask.completed,
            hx_post="/update",
            hx_include="closest li",
            cls="form-checkbox h-4 w-4 text-blue-600"
        ),
        Span(subtask.title, cls="flex-1"),
        Input(type="hidden", name="task_id", value=subtask.parent_id),
        Input(type="hidden", name="subtask_id", value=subtask.id)
    )

def task_checkbox(task: Task) -> Div:
    """Render just the task header section for partial updates"""
    return Div(
        id=f"task-header-{task.id}",
        cls="flex items-baseline gap-2"
    )(
        Input(
            type="checkbox",
            name="done",
            checked=task.completed,
            hx_post="/update",
            hx_include="closest div",
            cls="form-checkbox h-5 w-5 text-blue-600"
        ),
        H3(task.title, cls="flex-1 font-medium my-0"),
        Input(type="hidden", name="task_id", value=task.id)
    )

def tasks_container(task: Task) -> Li:
    """Render a task with its subtasks and add subtask button"""
    return Li(
        id=f"task-{task.id}",
        cls="mb-6 bg-white rounded-lg shadow-sm"
        )(
        # Parent task
        Div(cls="p-4 border-b")(
            task_checkbox(task),
        ),
        # Subtasks container
        Div(cls="p-4 bg-gray-50 rounded-b-lg space-y-4")(
            # Subtasks list
            Ul(
                *[subtask_container(subtask) 
                  for subtask in task.subtasks],
                cls="list-none p-0 mb-3"
            ),
            # Add subtask button
            Button(
                Span("+ Add Subtask", cls="text-sm"),
                hx_post=f"/tasks/{task.id}/subtasks",
                hx_prompt="Enter subtask title",
                cls="mt-3 ml-8 px-3 py-1 text-gray-600 hover:text-gray-800 \
                     border border-gray-300 rounded-md hover:bg-gray-50"
            ) if task.subtasks is not None else None,
            Div(cls="mt-4 px-2")(
                Div(cls="flex items-center gap-2")(
                    Input(
                        type="text",
                        name="note",
                        value=task.notes or "",
                        placeholder="Task note...",
                        hx_post="/update",
                        hx_include="closest div",
                        cls="flex-1 px-3 py-2 border rounded"
                    ),
                    Input(type="hidden", name="task_id", value=task.id)
                )
            )
        )
    )