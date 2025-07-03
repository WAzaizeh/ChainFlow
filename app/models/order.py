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
    order_id: str
    product_id: str
    product_name: str
    quantity: int
    created_at: datetime
    notes: Optional[str] = None
    units: Optional[List[str]] = None 
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OrderItem':
        return cls(
            id=data['$id'],
            order_id=data['order_id'],
            product_id=data['product_id'],
            product_name=data['product_name'],
            quantity=data['quantity'],
            notes=data.get('notes'),
            units=data.get('units'),  # Get units from data
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None
        )

@dataclass
class Order:
    id: str
    branch_id: str
    status: OrderStatus
    type: OrderType
    items: List[OrderItem]
    created_by: str
    created_at: datetime
    submitted_at: Optional[datetime]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        return cls(
            id=data['$id'],
            branch_id=data['branch_id'],
            status=OrderStatus(data['status']),
            type=OrderType(data['type']),
            items=data['items'] if 'items' in data else [],
            created_by=data['created_by'],
            created_at=datetime.fromisoformat(data['created_at']),
            submitted_at=datetime.fromisoformat(data['submitted_at']) if data.get('submitted_at') else None
        )