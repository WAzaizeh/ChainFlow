from core.app import rt
from fasthtml.common import *
from db.task_db import TaskDatabase
from models.task import Task, Subtask, TaskHistory
from layout.tasks import (
    task_checkbox,
    subtask_container,
    tasks_container
)
from layout.pages import TasksPage
from uuid import uuid4

db = TaskDatabase()

@rt('/tasks')
async def tasks_page():
    '''Main tasks page'''
    tasks = db.get_tasks()
    return TasksPage(tasks)

@rt('/tasks/{task_id}/toggle', methods=['POST'])
async def toggle_task(session, task_id: str):
    '''Toggle task completion status'''
    task = db.get_task(task_id)
    if not task:
        return 'Task not found', 404
    
    # Toggle task and all subtasks
    task.toggle_status()
    new_status = task.status
    for subtask in task.subtasks:
        subtask.status = new_status

    # Create history entry
    history = TaskHistory.create_status_change(
                task_id=task.id,
                subtask_id=None,
                new_status=new_status,
                user_id=session['user']['id']
            )
    
    success =  db.update_task(task)
    if success:
        db.add_history(history)
        return tasks_container(task)
    return 'Failed to update task', 500

@rt('/tasks/subtask/{subtask_id}/toggle', methods=['POST'])
async def toggle_subtask(req, session, subtask_id: str):
    '''Toggle subtask completion status and update parent task if needed'''
    data = await req.form()
    task_id = data['task_id']
    task =  db.get_task(task_id)
    if not task:
        return 'Task not found', 404
    
    # Find and toggle subtask
    subtask = next((st for st in task.subtasks if st.id == subtask_id), None)
    if not subtask:
        return 'Subtask not found', 404
    
    # Toggle subtask status
    subtask.toggle_status()
    histories = [
        TaskHistory.create_status_change(
            task_id=task.id,
            subtask_id=subtask.id,
            new_status=subtask.status,
            user_id=session['user']['id']
        )
    ]
    
    # Check if all subtasks are in the same state
    all_completed = all(st.status for st in task.subtasks)
    all_uncompleted = all(not st.status for st in task.subtasks)
    
    # Update task status if needed
    if all_completed and not task.status:
        task.status = True
        histories.append(
            TaskHistory.create_status_change(
                task_id=task.id,
                subtask_id=None,
                new_status=True,
                user_id=session['user']['id']
            )
        )
    elif all_uncompleted and task.status:
        task.status = False
        histories.append(
            TaskHistory.create_status_change(
                task_id=task.id,
                subtask_id=None,
                new_status=False,
                user_id=session['user']['id']
            )
        )
    
    # Update database
    success = db.update_task(task)
    if not success:
        return 'Failed to update task', 500

    for history in histories:
        db.add_history(history)
    
    # Update the task container
    return tasks_container(task)

@rt('/tasks/{task_id}/note', methods=['POST'])
async def update_task_note(req, session, task_id: str):
    '''Update task note'''
    data = await req.form()
    note = data['note'].strip()
    task =  db.get_task(task_id)
    if not task:
        return 'Task not found', 404
    
    # Add note and create history
    task.add_note(note)
    history = TaskHistory.create_note_change(
        task_id=task.id,
        note=note,
        user_id=session['user']['id']  # TODO: Add user authentication
    )
    
    # Update database
    success =  db.update_task(task)
    if success:
        db.add_history(history)
        return 'Note updated'
    return 'Failed to update note', 500

@rt('/tasks/{task_id}/subtasks', methods=['POST'])
async def add_subtask(req, task_id: str):
    '''Add new subtask to task'''
    title = req.form()['value'].strip()
    if not title:
        return 'Title required', 400
    
    task =  db.get_task(task_id)
    if not task:
        return 'Task not found', 404
    
    # Create new subtask with next order number
    max_order = max((st.order for st in task.subtasks), default=0)
    new_subtask = Subtask(
        id=str(uuid4()),
        task_id=task_id,
        title=title,
        status=False,
        order=max_order + 1
    )
    task.subtasks.append(new_subtask)
    
    # Update database
    success =  db.update_task(task)
    if success:
        return subtask_container(new_subtask)
    return 'Failed to add subtask', 500