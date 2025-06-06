from fasthtml.common import *
from typing import Dict, Any
from models.task import Task, SubTask
import json

def subtask_checkbox(subtask: SubTask) -> Form:
    """Render a subtask checkbox as its own form"""
    return Form(
        id=f"subtask-form-{subtask.id}",
        hx_post=f"/tasks/subtask/{subtask.id}/toggle",
        hx_trigger="change",
        cls="flex items-center gap-2"
    )(
        Input(
            type="checkbox",
            name="completed",
            checked=subtask.completed,
            cls="form-checkbox h-4 w-4 text-blue-600"
        ),
        Span(subtask.title, cls="flex-1"),
        Input(type="hidden", name="task_id", value=subtask.parent_id)
    )

def task_checkbox(task: Task) -> Form:
    """Render task checkbox with optimistic updates"""
    subtask_ids = [st.id for st in task.subtasks]
    return Form(
        id=f"task-form-{task.id}",
        hx_post=f"/tasks/{task.id}/toggle",
        hx_trigger="change",
        hx_swap="outerHTML",
        # Add optimistic attributes
        hx_indicator="this",
        **{
            f"hx-swap-oob": "true",
            # Target all subtasks for immediate update
            **{f"hx-select": f"#subtask-{id}" for id in subtask_ids}
        },
        cls="flex items-baseline gap-2"
    )(
        Input(
            type="checkbox",
            name="completed",
            checked=task.completed,
            cls="form-checkbox h-5 w-5 text-blue-600"
        ),
        H3(task.title, cls="flex-1 font-medium my-0")
    )

def task_note(task: Task) -> Form:
    """Render task note input as its own form"""
    return Form(
        id=f"task-note-{task.id}",
        hx_post=f"/tasks/{task.id}/note",
        cls="mt-4 px-2"
    )(
        Input(
            type="text",
            name="note",
            value=task.notes or "",
            placeholder="Task note...",
            cls="w-full px-3 py-2 border rounded"
        )
    )

def subtask_container(subtask: SubTask) -> Li:
    """Render a subtask row"""
    return Li(
        id=f"subtask-{subtask.id}",
        cls="ml-8 py-1 border-l-2 border-gray-200 pl-4"
    )(
        subtask_checkbox(subtask)
    )

def tasks_container(task: Task) -> Li:
    """Render a task with its subtasks and add subtask button"""
    return Li(
        id=f"task-{task.id}",
        cls="mb-6 bg-white rounded-lg shadow-sm"
    )(
        Div(cls="p-4 border-b")(
            task_checkbox(task)
        ),
        Div(cls="p-4 bg-gray-50 rounded-b-lg space-y-4")(
            Ul(
                *[subtask_container(st) for st in task.subtasks],
                cls="list-none p-0 mb-3"
            ),
            Button(
                Span("+ Add Subtask", cls="text-sm"),
                hx_post=f"/tasks/{task.id}/subtasks",
                hx_prompt="Enter subtask title",
                cls="mt-3 ml-8 px-3 py-1 text-gray-600 hover:text-gray-800 \
                     border border-gray-300 rounded-md hover:bg-gray-50"
            ) if task.subtasks is not None else None,
            task_note(task)
        )
    )