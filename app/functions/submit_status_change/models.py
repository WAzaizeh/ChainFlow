from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from enum import Enum

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
            id=str(uuid4()),
            task_id=task_id,
            change_type=ChangeType.STATUS,
            subtask_id=subtask_id,
            new_value=new_status,
            timestamp=datetime.now(),
            user_id=user_id
        )

    @classmethod
    def create_note_change(cls, task_id: str, note: str, user_id: str) -> 'TaskHistory':
        return cls(
            id=str(uuid4()),
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
            "$id": self.id,
            "task_id": self.task_id,
            "change_type": self.change_type.value,
            "subtask_id": self.subtask_id,
            "new_value": self.new_value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id
        }