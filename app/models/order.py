from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderType(Enum):
    REGULAR = "regular"
    URGENT = "urgent"
    SPECIAL = "special"

@dataclass
class OrderItem:
    id: str
    product_id: str
    quantity: int
    notes: Optional[str]
    created_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OrderItem':
        return cls(
            id=data['$id'],
            product_id=data['product_id'],
            quantity=data['quantity'],
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class Order:
    id: str
    branch_id: str  # Team/Branch ID
    status: OrderStatus
    type: OrderType
    items: List[OrderItem]
    created_by: str  # User ID
    created_at: datetime
    submitted_at: Optional[datetime]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        return cls(
            id=data['$id'],
            branch_id=data['branch_id'],
            status=OrderStatus(data['status']),
            type=OrderType(data['type']),
            items=data['items'],
            created_by=data['created_by'],
            created_at=datetime.fromisoformat(data['created_at']),
            submitted_at=datetime.fromisoformat(data['submitted_at']) if data.get('submitted_at') else None
        )