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


    def get_item(self, item_id: str) -> InventoryItem:
        """Get single inventory item"""
        doc = self.database.get_document(
            database_id=self.database_id,
            collection_id='inventory',
            document_id=item_id
        )
        return InventoryItem.from_dict(doc)
        
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
            quantity_change=quantity,
            unit_change=unit, #TODO handle unit changes properly
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