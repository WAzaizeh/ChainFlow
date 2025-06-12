from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from appwrite.id import ID

@dataclass
class InventoryItem:
    id: str
    name: str
    quantity: int
    unit: Optional[str]
    last_updated: datetime
    
    @property
    def has_unit(self) -> bool:
        """Check if item uses units"""
        return bool(self.unit)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryItem':
        """Create item from Appwrite document"""
        return cls(
            id=data['$id'],
            name=data['name'],
            quantity=data['quantity'],
            unit=data.get('unit', None),
            last_updated=data['last_updated']
        )
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for Appwrite"""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "last_updated": self.last_updated
        }

@dataclass
class InventoryChange:
    id: str
    item_id: str
    quantity_change: int
    unit_change: Optional[str]
    timestamp: datetime
    user_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryChange':
        """Create change from Appwrite document"""
        return cls(
            id=data["id"],
            item_id=data['item_id'],
            quantity_change=data['quantity_change'],
            unit_change=data.get('unit_change'),
            timestamp=data['timestamp'],
            user_id=data['user_id']
        )
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for Appwrite"""
        return {
            "item_id": self.item_id,
            "quantity_change": self.quantity_change,
            "unit_change": self.unit_change,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "user_id": self.user_id
        }