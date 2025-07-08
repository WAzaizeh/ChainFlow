"""
SSE Manager for handling real-time task updates across multiple users
"""
import asyncio
import json
from typing import Dict, Set, Any
from datetime import datetime
from fasthtml.common import to_xml
from models.task import Task, Subtask
from layout.tasks import task_checkbox, subtask_checkbox, task_note_form

class SSEManager:
    """Manages SSE connections and broadcasts updates to all connected clients"""
    
    def __init__(self):
        self._connections: Set[asyncio.Queue] = set()
        self._task_subscribers: Dict[str, Set[asyncio.Queue]] = {}
    
    def add_connection(self, queue: asyncio.Queue):
        """Add a new SSE connection"""
        self._connections.add(queue)
    
    def remove_connection(self, queue: asyncio.Queue):
        """Remove an SSE connection"""
        self._connections.discard(queue)
        # Remove from task-specific subscribers
        for subscribers in self._task_subscribers.values():
            subscribers.discard(queue)
    
    def subscribe_to_task(self, task_id: str, queue: asyncio.Queue):
        """Subscribe a connection to updates for a specific task"""
        if task_id not in self._task_subscribers:
            self._task_subscribers[task_id] = set()
        self._task_subscribers[task_id].add(queue)
    
    async def broadcast_task_update(self, task: Task, update_type: str, subtask_id: str = None):
        """Broadcast task updates to all connected clients"""
        events = []
        
        if update_type == "task_status":
            # Send updated task checkbox
            events.append({
                "data": to_xml(task_checkbox(task)),
                "event": f"TaskStatusUpdate_{task.id}",
                "id": f"{task.id}_{datetime.now().timestamp()}"
            })
            
        elif update_type == "subtask_status" and subtask_id:
            # Send updated subtask checkbox
            subtask = next((st for st in task.subtasks if st.id == subtask_id), None)
            if subtask:
                events.append({
                    "data": to_xml(subtask_checkbox(subtask)),
                    "event": f"SubtaskStatusUpdate_{subtask_id}",
                    "id": f"{subtask_id}_{datetime.now().timestamp()}"
                })
            
            # Also send updated task checkbox if parent status changed
            events.append({
                "data": to_xml(task_checkbox(task)),
                "event": f"TaskStatusUpdate_{task.id}",
                "id": f"{task.id}_{datetime.now().timestamp()}"
            })
            
        elif update_type == "task_note":
            # Send updated note form
            events.append({
                "data": to_xml(task_note_form(task)),
                "event": f"TaskNoteUpdate_{task.id}",
                "id": f"{task.id}_note_{datetime.now().timestamp()}"
            })
        
        # Broadcast to all subscribers
        await self._broadcast_events(events)
    
    async def _broadcast_events(self, events: list):
        """Send events to all connected clients"""
        if not events:
            return
            
        disconnected = set()
        
        for queue in self._connections:
            try:
                for event in events:
                    await queue.put(event)
            except:
                # Connection is broken, mark for removal
                disconnected.add(queue)
        
        # Clean up disconnected clients
        for queue in disconnected:
            self.remove_connection(queue)

# Global SSE manager instance
sse_manager = SSEManager()
