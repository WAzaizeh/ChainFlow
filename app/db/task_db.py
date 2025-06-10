from appwrite.query import Query
from typing import List, Optional
from core.appwrite_client import get_database
from core.config import settings
from appwrite.id import ID
from models.task import (
    Task,
    Subtask,
    TaskHistory,
)

class TaskDatabase:
    def __init__(self):
        self.database = get_database()
        self.database_id = settings.DATABASE_ID

    def get_subtasks(self, task_id: str) -> List[Subtask]:
        """Fetch subtasks for a specific task"""
        result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='subtasks',
            queries=[
                Query.equal('task_id', task_id),
                Query.order_asc('order')
            ]
        )
        return [Subtask.from_dict(doc) for doc in result['documents']]
        
    def get_task(self, task_id: str) -> Optional[Task]:
        """Fetch a single task by ID"""
        task_doc = self.database.get_document(
            database_id=self.database_id,
            collection_id='tasks',
            document_id=task_id
        )
        # Get subtasks for this task
        task_doc['subtasks'] = self.get_subtasks(task_id)

        return Task.from_dict(task_doc)

        
    def get_tasks(self) -> List[Task]:
        """Fetch all tasks"""
        tasks_result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='tasks'
        )
        tasks = []
        for task_doc in tasks_result['documents']:
            # Get subtasks for each task
            task_doc['subtasks'] = self.get_subtasks(task_doc['$id'])
            # Add subtasks to task document
            tasks.append(Task.from_dict(task_doc))
        return tasks
    
    def update_task(self, task: Task) -> bool:
        """Update task document"""
        self.database.update_document(
            database_id=self.database_id,
            collection_id='tasks',
            document_id=task.id,
            data=task.to_json()
        )
        for subtask in task.subtasks:
            self.database.update_document(
                database_id=self.database_id,
                collection_id='subtasks',
                document_id=subtask.id,
                data=subtask.to_json()
            )
        return True
    
    def add_history(self, history: TaskHistory) -> bool:
        """Add new history entry"""
        self.database.create_document(
            database_id=self.database_id,
            collection_id='task_history',
            document_id=history.id if history.id else ID.unique(),
            data=history.to_json()
        )
        return True
    
    def get_task_history(self, task_id: str) -> List[TaskHistory]:
        """Fetch history for a task"""
        result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='task_history',
            queries=[
                Query.equal('task_id', task_id),
                Query.orderDesc('timestamp')
            ]
        )
        return [TaskHistory.from_dict(doc) for doc in result['documents']]

        
    def get_task_history(self, task_id: str) -> List[TaskHistory]:
        """Fetch history for a task"""
        result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='task_history',
            queries=[
                Query.equal('task_id', task_id),
                Query.orderDesc('timestamp')
            ]
        )
        return [TaskHistory.from_dict(doc) for doc in result['documents']]