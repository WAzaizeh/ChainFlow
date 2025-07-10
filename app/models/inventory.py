from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from appwrite.id import ID
from enum import Enum

class StorageLocation(Enum):
    WAREHOUSE = "warehouse"
    BACKOFFICE = "backoffice"
    KITCHEN = "kitchen"

class Branch(Enum):
    Plano = "Plano"

@dataclass
class InventoryItem:
    id: str
    name: str
    quantity: float
    primary_unit: str
    storage: StorageLocation
    last_updated: datetime
    branch: Branch = Branch.Plano  # Default branch

    @classmethod
    def create_new(
            cls, name: str, quantity: float, primary_unit: str, 
            branch: str = Branch.Plano.value,
            storage: str = StorageLocation.WAREHOUSE.value,
            last_updated: Optional[datetime] = None
            ) -> 'InventoryItem':
        """Create a new inventory item"""
        return cls(
            id=ID.unique(),
            name=name,
            quantity=quantity,
            primary_unit=primary_unit,
            branch=branch,
            storage=storage,
            last_updated=last_updated if last_updated else datetime.now().isoformat()
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryItem':
        """Create item from Appwrite document"""
        return cls(
            id=data['$id'],
            name=data['name'],
            quantity=float(data['quantity']),
            primary_unit=data['primary_unit'],
            branch=data['branch'],
            storage=data['storage'],
            last_updated=data['last_updated']
        )
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for Appwrite"""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "primary_unit": self.primary_unit,
            "branch": self.branch,
            "storage": self.storage,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated
        }

@dataclass
class ItemUnit:
    id: str
    item_id: str
    unit_name: str
    conversion_to_primary: float  # How many primary units = 1 of this unit
    last_updated: datetime = None

    @classmethod
    def create_new(
        cls, item_id: str, unit_name: str,
        conversion_to_primary: float,
        last_updated: Optional[datetime] = None
        ) -> 'ItemUnit':
        """Create a new secondary unit for an item"""
        return cls(
            id=ID.unique(),
            item_id=item_id,
            unit_name=unit_name,
            conversion_to_primary=conversion_to_primary,
            last_updated=last_updated if last_updated else datetime.now().isoformat()
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemUnit':
        """Create unit from Appwrite document"""
        return cls(
            id=data['$id'],
            item_id=data['item_id'],
            unit_name=data['unit_name'],
            conversion_to_primary=float(data['conversion_to_primary']),
            last_updated=data['last_updated']
        )
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for Appwrite"""
        return {
            "item_id": self.item_id,
            "unit_name": self.unit_name,
            "conversion_to_primary": self.conversion_to_primary,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated
        }

@dataclass
class InventoryChange:
    id: str
    item_id: str
    change_quantity: float
    timestamp: datetime
    user_id: str
    change_unit: Optional[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryChange':
        """Create change from Appwrite document"""
        return cls(
            id=data["$id"],
            item_id=data['item_id'],
            change_quantity=data['change_quantity'],
            change_unit=data.get('change_unit'),
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