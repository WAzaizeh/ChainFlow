from fasthtml.common import *
from models.task import Task, Subtask

def subtask_checkbox(subtask: Subtask) -> Form:
    """Render a subtask checkbox as its own form"""
    return Form(
        id=f"subtask-form-{subtask.id}",
        hx_post=f"/tasks/subtask/{subtask.id}/toggle",
        hx_trigger="change",
        hx_swap="outerHTML",
        hx_target=f"#subtask-form-{subtask.id}",
        cls="flex items-center gap-2",
        sse_swap=f"SubtaskStatusUpdate_{subtask.id}"
    )(
        Input(
            type="checkbox",
            name="status",
            checked=subtask.status,
            cls="form-checkbox h-4 w-4 text-blue-600"
        ),
        Span(subtask.title, cls="flex-1"),
        Input(type="hidden", name="task_id", value=subtask.task_id)
    )

def task_checkbox(task: Task) -> Form:
    """Render task checkbox with optimistic updates"""
    return Form(
        id=f"task-form-{task.id}",
        hx_post=f"/tasks/{task.id}/toggle",
        hx_trigger="change",
        hx_swap="outerHTML",
        hx_indicator="this",
        hx_target=f"#task-form-{task.id}",
        cls="flex items-baseline gap-2",
        sse_swap=f"TaskStatusUpdate_{task.id}"
    )(
        Input(
            type="checkbox",
            name="status",
            checked=task.status,
            cls="form-checkbox h-5 w-5 text-blue-600"
        ),
        H3(task.title, cls="flex-1 font-medium my-0")
    )

def task_note_form(task: Task) -> Form:
    """Render task note form with SSE updates - follows same pattern as checkboxes"""
    return Form(
        id=f"task-note-form-{task.id}",
        cls="mt-4 px-2 ml-4",
        sse_swap=f"TaskNoteUpdate_{task.id}"
    )(
        Textarea(
            id=f"note-textarea-{task.id}",
            name="note",
            placeholder="Add note...",
            cls="w-full px-3 py-2 border rounded min-h-[100px]",
            hx_post=f"/tasks/{task.id}/notes/update",
            hx_trigger="keyup changed delay:500ms",
            hx_include=f"#task-note-form-{task.id}"
        )(task.notes or "")
    )

def subtasks_list(subtask: Subtask) -> Li:
    """Render a subtask row with proper ordering and SSE support"""
    return Li(
        id=f"subtask-{subtask.id}",
        cls="ml-8 py-1 border-l-2 border-gray-200 pl-4 list-none",
        style=f"order: {subtask.order}"  # Use order field for positioning
    )(
        subtask_checkbox(subtask)
    )

def tasks_container(task: Task) -> Li:
    """Render a task with its subtasks and add subtask button"""
    sorted_subtasks = sorted(task.subtasks, key=lambda x: x.order)
    return Li(
        id=f"task-{task.id}",
        cls="mb-6 bg-white rounded-lg shadow-sm list-none"
    )(
        Div(cls="p-4 border-b")(
            task_checkbox(task)
        ),
        Div(cls="p-4 bg-gray-50 rounded-b-lg space-y-4")(
            Ul(
                *[subtasks_list(st) for st in sorted_subtasks],
                cls="list-none p-0 mb-3"
            ),
            task_note_form(task)
        )
    )

