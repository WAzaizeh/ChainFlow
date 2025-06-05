from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class SubTask:
    id: str
    parent_id: str
    title: str
    order: int
    completed: bool
    completed_at: Optional[datetime] = None

@dataclass
class Task:
    id: str
    title: str
    completed: bool
    subtasks: List[SubTask]
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    
    def complete(self) -> None:
        """Complete task and all subtasks"""
        self.completed = True
        self.completed_at = datetime.now()
        for subtask in self.subtasks:
            subtask.completed = True
            subtask.completed_at = self.completed_at
            
    def check_subtasks(self) -> None:
        """Mark task as complete if all subtasks are complete"""
        if all(st.completed for st in self.subtasks):
            self.complete()