from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from appwrite.id import ID

@dataclass
class Subtask:
    id: str
    title: str
    task_id: str
    status: bool
    last_updated: datetime
    order: int

    def toggle_status(self) -> None:
        """Toggle subtask completion status"""
        self.status = not self.status

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subtask':
        """Create Subtask from Appwrite document"""
        return cls(
            id=data["$id"],
            task_id=data['task_id'],
            title=data['title'],
            status=data['status'],
            last_updated=data['last_updated'],
            order=data['order']
        )

    def to_json(self) -> Dict[str, Any]:
        """Convert subtask to JSON-compatible dict"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status,
            "last_updated": self.last_updated,
            "order": self.order
        }

@dataclass
class Task:
    id: str
    title: str
    subtasks: List[Subtask]
    notes: str
    status: bool
    last_updated: datetime

    def toggle_status(self) -> None:
        """Toggle task completion status"""
        self.status = not self.status
        self.last_updated = datetime.now()
    
    def add_note(self, note: str) -> None:
        """Append a new note"""
        self.notes = note if note else self.notes
        self.last_updated = datetime.now()

    @classmethod
    def create_new(cls, title: str) -> 'Task':
        """Create a new task with default values"""
        return cls(
            id=ID.unique(),
            title=title,
            subtasks=[],
            notes="",
            status=False,
            last_updated=datetime.now()
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from Appwrite document"""
        return cls(
            id=data.get('$id', data.get('id')),  # Handle both $id and id
            title=data['title'],
            subtasks=data['subtasks'],
            notes=data['notes'],
            status=data['status'],
            last_updated=data['last_updated']
        )

    def to_json(self) -> Dict[str, Any]:
        """Convert task to JSON-compatible dict"""
        return {
            "title": self.title,
            "notes": self.notes,
            "status": self.status,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated,
        }

class ChangeType(Enum):
    STATUS = "status"
    NOTE = "note"

@dataclass
class TaskHistory:
    id: str
    task_id: str
    change_type: ChangeType
    subtask_id: Optional[str]
    new_value: Any
    timestamp: datetime
    user_id: str

    @classmethod
    def create_status_change(cls, task_id: str, subtask_id: Optional[str], 
                           new_status: bool, user_id: str) -> 'TaskHistory':
        return cls(
            id=ID.unique(),
            task_id=task_id,
            change_type=ChangeType.STATUS,
            subtask_id=subtask_id,
            new_value=str(new_status), # Convert bool to str for consistency
            timestamp=datetime.now(),
            user_id=user_id
        )

    @classmethod
    def create_note_change(cls, task_id: str, note: str, user_id: str) -> 'TaskHistory':
        return cls(
            id=ID.unique(),
            task_id=task_id,
            change_type=ChangeType.NOTE,
            subtask_id=None,
            new_value=note,
            timestamp=datetime.now(),
            user_id=user_id
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskHistory':
        """Create TaskHistory from Appwrite document"""
        return cls(
            id=data.get('$id', data.get('id')),  # Handle both $id and id
            task_id=data['task_id'],
            change_type=ChangeType(data['change_type']),
            subtask_id=data.get('subtask_id'),
            new_value=data['new_value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            user_id=data['user_id']
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "change_type": self.change_type.value,
            "subtask_id": self.subtask_id,
            "new_value": self.new_value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id
        }