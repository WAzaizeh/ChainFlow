from fasthtml.common import *
from models.task import Task, Subtask

def subtask_checkbox(subtask: Subtask) -> Form:
    """Render a subtask checkbox as its own form"""
    return Form(
        id=f"subtask-form-{subtask.id}",
        hx_post=f"/tasks/subtask/{subtask.id}/toggle",
        hx_trigger="change",
        hx_swap="outerHTML",
        hx_target=f"#task-{subtask.task_id}",  # Target entire task content
        cls="flex items-center gap-2"
    )(
        Input(
            type="checkbox",
            name="status",  # changed from completed to status
            checked=subtask.status,
            cls="form-checkbox h-4 w-4 text-blue-600"
        ),
        Span(subtask.title, cls="flex-1"),
        Input(type="hidden", name="task_id", value=subtask.task_id)  # changed from parent_id
    )

def task_checkbox(task: Task) -> Form:
    """Render task checkbox with optimistic updates"""
    subtask_ids = [st.id for st in task.subtasks]
    return Form(
        id=f"task-form-{task.id}",
        hx_post=f"/tasks/{task.id}/toggle",
        hx_trigger="change",
        hx_swap="outerHTML",
        hx_indicator="this",
        hx_target=f"#task-{task.id}",  # Target the entire task container
        cls="flex items-baseline gap-2"
    )(
        Input(
            type="checkbox",
            name="status",
            checked=task.status,
            cls="form-checkbox h-5 w-5 text-blue-600"
        ),
        H3(task.title, cls="flex-1 font-medium my-0")
    )

def task_note(task: Task) -> Form:
    """Render task note input as its own form"""
    return Form(
        id=f"task-note-{task.id}",
        hx_post=f"/tasks/{task.id}/note",
        hx_trigger="input changed delay:500ms",
        hx_swap="none",
        cls="mt-4 px-2"
    )(
        Input(
            type="text",
            name="note",
            value=task.notes,
            placeholder="Add note...",
            cls="w-full px-3 py-2 border rounded"
        )
    )

def subtask_container(subtask: Subtask) -> Li:
    """Render a subtask row with proper ordering"""
    return Li(
        id=f"subtask-{subtask.id}",
        cls="ml-8 py-1 border-l-2 border-gray-200 pl-4",
        style=f"order: {subtask.order}"  # Use order field for positioning
    )(
        subtask_checkbox(subtask)
    )

def tasks_container(task: Task) -> Li:
    """Render a task with its subtasks and add subtask button"""
    sorted_subtasks = sorted(task.subtasks, key=lambda x: x.order)
    return Li(
        id=f"task-{task.id}",
        cls="mb-6 bg-white rounded-lg shadow-sm"
    )(
        Div(cls="p-4 border-b")(
            task_checkbox(task)
        ),
        Div(cls="p-4 bg-gray-50 rounded-b-lg space-y-4")(
            Ul(
                *[subtask_container(st) for st in sorted_subtasks],
                cls="list-none p-0 mb-3"
            ),
            Button(
                Span("+ Add Subtask", cls="text-sm"),
                hx_post=f"/tasks/{task.id}/subtasks",
                hx_prompt="Enter subtask title",
                cls="mt-3 ml-8 px-3 py-1 text-gray-600 hover:text-gray-800 \
                     border border-gray-300 rounded-md hover:bg-gray-50"
            ),
            task_note(task)
        )
    )