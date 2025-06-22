from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from appwrite.id import ID
from enum import Enum

@dataclass
class InventoryItem:
    id: str
    name: str
    quantity: int
    units: list[str]
    last_updated: datetime

    @classmethod
    def create_new(cls, name: str, quantity: int, units: list[str] = None) -> 'InventoryItem':
        """Create a new inventory item"""
        return cls(
            id=ID.unique(),
            name=name,
            quantity=quantity,
            units=units if units is not None else [],
            last_updated=datetime.now()
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryItem':
        """Create item from Appwrite document"""
        return cls(
            id=data['$id'],
            name=data['name'],
            quantity=data['quantity'],
            units=data.get('units', None),
            last_updated=data['last_updated']
        )
    
    def get_unit_names(self) -> list[str]:
        """Get units as a list, defaulting to empty if None"""
        return self.units if self.units is not None else []
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for Appwrite"""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "units": self.units,
            "last_updated": self.last_updated
        }

@dataclass
class ItemUnit:
    id: str
    item_id: str
    unit_name: str
    tier: int  # 0=primary, 1=secondary
    conversion: float  # conversion rate to previous tier
    last_updated: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemUnit':
        """Create unit from Appwrite document"""
        return cls(
            id=data['$id'],
            item_id=data['item_id'],
            unit_name=data['unit_name'],
            tier=data['tier'],
            conversion=data['conversion'],
            last_updated=data['last_updated']
        )
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for Appwrite"""
        return {
            "item_id": self.item_id,
            "unit_name": self.unit_name,
            "tier": self.tier,
            "conversion": self.conversion,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated
        }
    
    def is_primary(self) -> bool:
        """Check if this is a primary unit"""
        return self.tier == 0

@dataclass
class InventoryChange:
    id: str
    item_id: str
    change_quantity: int
    change_unit: Optional[str]
    timestamp: datetime
    user_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryChange':
        """Create change from Appwrite document"""
        return cls(
            id=data["id"],
            item_id=data['item_id'],
            change_quantity=data['change_quantity'],
            change_unit=data.get('change_unitz'),
            timestamp=data['timestamp'],
            user_id=data['user_id']
        )
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for Appwrite"""
        return {
            "item_id": self.item_id,
            "change_quantity": self.change_quantity,
            "change_unit": self.change_unit,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "user_id": self.user_id
        }