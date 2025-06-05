from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Checkin:
    """Represents a change in task or subtask status"""
    id: str  # Composite ID: {user_id}-{task_id}-{YYYY-MM-DD}[-{subtask_id}]
    user_id: str
    task_id: str
    completed: bool
    note: Optional[str] = None
    subtask_id: Optional[str] = None
    updated_at: datetime = datetime.now()

    def create_id(self) -> None:
        """Generate and set composite ID for checkin using instance values"""
        base_id = f"{self.user_id}-{self.task_id}-{self.updated_at.date().isoformat()}"
        self.id = f"{base_id}-{self.subtask_id}" if self.subtask_id else base_id