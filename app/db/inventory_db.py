from typing import List, Optional, Dict
from datetime import datetime
from appwrite.query import Query
from appwrite.id import ID
from models.inventory import InventoryItem, InventoryChange, ItemUnit, StorageLocation
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
    
    def get_item_secondary_units(self, item_id: str) -> List[ItemUnit]:
        """Get all secondary units for a specific inventory item"""
        try:
            result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='item_units',
                queries=[Query.equal('item_id', item_id)]
            )
            return [ItemUnit.from_dict(doc) for doc in result['documents']]
        except Exception as e:
            print(f"Error fetching units for item {item_id}: {e}")
            return []
    
    def convert_to_primary_unit(self, item_id: str, secondary_quantity: float, secondary_unit: str) -> float:
        """Convert secondary unit quantity to primary unit quantity"""
        units = self.get_item_secondary_units(item_id)
        unit_obj = next((u for u in units if u.unit_name == secondary_unit), None)
        
        if not unit_obj:
            raise ValueError(f"Secondary unit '{secondary_unit}' not found for item {item_id}")
        
        return secondary_quantity * unit_obj.conversion_to_primary
    
    def update_item_quantity(self, item_id: str, primary_quantity_change: float, 
                           original_unit: str, original_quantity: float,
                           storage: str, timestamp: datetime, user_id: str) -> bool:
        """Update item quantity with pre-calculated primary unit change"""
        item = self.get_item(item_id)
        if not item:
            raise DocumentNotFoundError(f"Item {item_id} not found")

        # Update the item's quantity and storage
        item.quantity += primary_quantity_change
        item.storage = storage
        item.last_updated = timestamp

        # Create change record with original unit and quantity
        change = InventoryChange(
            id=ID.unique(),
            item_id=item_id,
            change_quantity=original_quantity,  # Store original quantity entered
            change_unit=original_unit,          # Store original unit used
            timestamp=timestamp,
            user_id=user_id
        )

        try:
            # Update item in database
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
        except Exception as e:
            print(f"Error updating item {item_id}: {e}")
            return False
    
    def add_item_with_units(self, name: str, initial_quantity: float, 
                           primary_unit: str, storage: str = StorageLocation.KITCHEN.value,
                           additional_units: List[Dict] = None) -> str:
        """Add new item with its units and storage location"""
        # Create the item
        item = InventoryItem.create_new(
            name=name, 
            quantity=initial_quantity, 
            primary_unit=primary_unit,
            storage=storage
        )
        
        # Store item
        self.database.create_document(
            database_id=self.database_id,
            collection_id='inventory',
            document_id=item.id,
            data=item.to_json()
        )
        
        # Create additional units if provided
        if additional_units:
            for unit_data in additional_units:
                unit_obj = ItemUnit.create_new(
                    item_id=item.id,
                    unit_name=unit_data['name'],
                    conversion_to_primary=float(unit_data['conversion'])
                )
                
                self.database.create_document(
                    database_id=self.database_id,
                    collection_id='item_units',
                    document_id=unit_obj.id,
                    data=unit_obj.to_json()
                )
        
        return item.id