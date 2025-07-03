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
from datetime import datetime
from logging import getLogger
logger = getLogger(__name__)

class TaskDatabase:
    def __init__(self):
        self.database = get_database()
        self.database_id = settings.TASKS_DATABASE_ID

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
            # Get subtasks to task document
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
                Query.order_desc('timestamp')
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
                Query.order_desc('timestamp')
            ]
        )
        return [TaskHistory.from_dict(doc) for doc in result['documents']]
    
    def archive_subtasks(self, task_id: str, archive_timestamp: str) -> List[dict]:
        """Archive subtasks for a specific task"""
        try:
            subtasks = self.get_subtasks(task_id)
            archived_subtasks = []
            
            for subtask in subtasks:
                # Create archive entry for each subtask
                archived = self.database.create_document(
                    database_id=self.database_id,
                    collection_id='subtask_archives',
                    document_id=ID.unique(),
                    data={
                        'task_id': task_id,
                        'subtask_id': subtask.id,
                        'archive_timestamp': archive_timestamp,
                        'subtask_data': subtask.to_json(),
                        'archived_at': datetime.now().isoformat()
                    }
                )
                archived_subtasks.append(archived)
                
            logger.debug(f"Archived {len(archived_subtasks)} subtasks for task {task_id}")
            return archived_subtasks
            
        except Exception as e:
            logger.error(f"Failed to archive subtasks for task {task_id}: {e}")
            return []

    def reset_subtasks(self, task_id: str) -> bool:
        """Reset all subtasks for a specific task"""
        try:
            subtasks = self.get_subtasks(task_id)
            
            for subtask in subtasks:
                self.database.update_document(
                    database_id=self.database_id,
                    collection_id='subtasks',
                    document_id=subtask.id,
                    data={
                        'status': False,
                        'last_updated': datetime.now().isoformat()
                    }
                )
                
            logger.debug(f"Reset {len(subtasks)} subtasks for task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset subtasks for task {task_id}: {e}")
            return False

    def archive_tasks(self) -> bool:
        """Archive tasks and their subtasks"""
        try:
            tasks_result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='tasks'
            )
            
            archive_timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            
            for task_doc in tasks_result['documents']:
                task_id = task_doc['$id']
                
                # Archive subtasks first
                archived_subtasks = self.archive_subtasks(task_id, archive_timestamp)
                
                # Store task archive with reference to archived subtasks
                self.database.create_document(
                    database_id=self.database_id,
                    collection_id='task_archives',
                    document_id=ID.unique(),
                    data={
                        'task_id': task_id,
                        'archive_timestamp': archive_timestamp,
                        'task_data': task_doc,
                        'subtasks_data': [s['$id'] for s in archived_subtasks],
                        'archived_at': datetime.now().isoformat()
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to archive tasks: {e}")
            return False

    def reset_tasks(self) -> bool:
        """Reset tasks and their subtasks"""
        try:
            tasks_result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='tasks'
            )
            
            for task_doc in tasks_result['documents']:
                task_id = task_doc['$id']
                
                # Reset main task
                self.database.update_document(
                    database_id=self.database_id,
                    collection_id='tasks',
                    document_id=task_id,
                    data={
                        'status': False,
                        'notes': "",
                        'last_updated': datetime.now().isoformat()
                    }
                )
                
                # Reset associated subtasks
                self.reset_subtasks(task_id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to reset tasks: {e}")
            return False