from typing import List, Optional
from datetime import datetime
from appwrite.query import Query
from appwrite.id import ID
from models.inventory import InventoryItem, InventoryChange
from core.appwrite_client import get_database
from core.config import settings

class DocumentNotFoundError(Exception):
    """Custom exception for document not found errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class InventoryDatabase:
    def __init__(self):
        self.database = get_database()
        self.database_id = settings.INVENTORY_DATABASE_ID

    def get_all_items(self) -> list[InventoryItem]:
        """Get all inventory items"""
        try:
            result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='inventory'
            )
            return [InventoryItem.from_dict(doc) for doc in result['documents']]
        except Exception as e:
            return []

    def search_items(self, query: str) -> List[InventoryItem]:
        """Search inventory items by name"""
        result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='inventory',
            queries=[
                Query.search('name', query),
                Query.limit(10)
            ]
        )
        return [InventoryItem.from_dict(doc) for doc in result['documents']]
    
    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get inventory item object by ID"""
        try:
            doc = self.database.get_document(
                database_id=self.database_id,
                collection_id='inventory',
                document_id=item_id
            )
            return InventoryItem.from_dict(doc)
        except Exception as e:
            return None
    
    def get_item_units(self, item_id: str) -> List[InventoryItem]:
        """Get all units for a specific inventory item"""
        try:
            result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='item_units',
                queries=[Query.equal('item_id', item_id)]
            )
            return [InventoryItem.from_dict(doc) for doc in result['documents']]
        except Exception as e:
            return []
    
    def convert_quantity(self, item_id: str, quantity: float, 
                        from_unit: str, to_unit: str) -> float:
        """Convert quantity between units"""
        units = self.get_item_units(item_id)
        
        from_unit_obj = next((u for u in units if u.unit_name == from_unit), None)
        to_unit_obj = next((u for u in units if u.unit_name == to_unit), None)
        
        if not from_unit_obj or not to_unit_obj:
            raise ValueError(f"Units not found: {from_unit} or {to_unit}")
            
        # Convert to primary first
        primary_quantity = quantity
        if not from_unit_obj.is_primary():
            primary_quantity = quantity * from_unit_obj.conversion
            
        # Then convert to target unit
        if not to_unit_obj.is_primary():
            return primary_quantity / to_unit_obj.conversion
            
        return primary_quantity
        
    def update_item_quantity(
            self, 
            item_id: str, 
            quantity: int, 
            unit: str,
            timestamp: datetime,
            user_id: str
            ) -> bool:
        """Update item quantity and track change"""
        # Get current item state
        item = self.get_item(item_id)
        if not item:
            raise DocumentNotFoundError(f"Item {item_id} not found")

        # Create change record
        change = InventoryChange(
            id=ID.unique(),
            item_id=item_id,
            change_quantity=quantity,
            change_unit=unit,
            timestamp=timestamp,
            user_id=user_id
        )

        # Update database
        self.database.update_document(
            database_id=self.database_id,
            collection_id='inventory',
            document_id=item_id,
            data=item.to_json()
        )

        # Log change
        self.database.create_document(
            database_id=self.database_id,
            collection_id='inventory_changes',
            document_id=change.id,
            data=change.to_json()
        )

        return True