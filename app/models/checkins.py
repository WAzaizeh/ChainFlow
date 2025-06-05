from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4
from dataclasses import field

@dataclass
class Checkin:
    """Represents a change in task or subtask status"""
    user_id: str
    task_id: str
    completed: bool
    note: Optional[str] = None
    subtask_id: Optional[str] = None
    completed_at: datetime = datetime.now()
    id: Optional[str] = None
    id: str = field(default_factory=lambda: uuid4().hex)