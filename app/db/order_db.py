from typing import List, Optional
from models.order import Order, OrderItem, OrderStatus, OrderType
from core.appwrite_client import get_database
from core.config import settings
from appwrite.query import Query
from appwrite.id import ID
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderDatabase:
    def __init__(self):
        self.database = get_database()
        self.database_id = settings.DATABASE_ID

    def create_order(self, branch_id: str, user_id: str) -> Order:
        """Create a new draft order"""
        try:
            order_data = self.database.create_document(
                database_id=self.database_id,
                collection_id='orders',
                document_id=ID.unique(),
                data={
                    'branch_id': branch_id,
                    'status': OrderStatus.DRAFT.value,
                    'type': OrderType.REGULAR.value,
                    'created_by': user_id,
                    'created_at': datetime.now().isoformat(),
                    'submitted_at': None,
                }
            )
            logger.info(f"Created new draft order {order_data['$id']} for branch {branch_id}")
            return Order.from_dict(order_data)
            
        except Exception as e:
            logger.error(f"Failed to create draft order: {e}")
            raise

    def get_branch_orders(self, branch_id: str) -> List[Order]:
        """Get all orders for a branch"""
        result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='orders',
            queries=[
                Query.equal('branch_id', branch_id),
                Query.order_desc('created_at')
            ]
        )
        if 'documents' in result:
            # fetch order items for each order
            for doc in result['documents']:
                items_result = self.database.list_documents(
                    database_id=self.database_id,
                    collection_id='order_items',
                    queries=[Query.equal('order_id', doc['$id'])]
                )
                doc['items'] = [OrderItem.from_dict(item) for item in items_result['documents']]
        return [Order.from_dict(doc) for doc in result['documents']]

    def get_draft_order(self, branch_id: str) -> Optional[Order]:
        """Get active draft order for branch if exists"""
        result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='orders',
            queries=[
                Query.equal('branch_id', branch_id),
                Query.equal('status', OrderStatus.DRAFT.value),
                Query.order_desc('created_at'),
                Query.limit(1)
            ]
        )
        docs = result.get('documents', [])
        if not docs:
            return None
        
        # fetch order items for the draft order
        items_result = self.database.list_documents(
            database_id=self.database_id,
            collection_id='order_items',
            queries=[Query.equal('order_id', docs[0]['$id'])]
        )
        docs[0]['items'] = [OrderItem.from_dict(item) for item in items_result['documents']]
        return Order.from_dict(docs[0]) if docs else None

    def add_order_item(self, order_id: str, product_name : str, product_id: str, quantity: int, units: list[str], notes: Optional[str] = None) -> OrderItem:
        """Add item to order"""
        print(f'{product_name=}')
        try:
            item_data = self.database.create_document(
                database_id=self.database_id,
                collection_id='order_items',
                document_id=ID.unique(),
                data={
                'order_id': order_id,
                'product_name': product_name,
                'product_id': product_id,
                'quantity': quantity,
                'units': units,
                'notes': notes,
                'created_at': datetime.now().isoformat(),
            }
            )
            return OrderItem.from_dict(item_data)
        except Exception as e:
            logger.error(f"Failed to add item to order {order_id}: {e}")

    def submit_order(self, order_id: str) -> Order:
        """Submit draft order"""
        order_data = self.database.update_document(
            database_id=self.database_id,
            collection_id='orders',
            document_id=order_id,
            data={
                'status': OrderStatus.SUBMITTED.value,
                'submitted_at': datetime.now().isoformat()
            }
        )
        return Order.from_dict(order_data)

    def update_order_type(self, order_id: str, order_type: OrderType) -> Order:
        """Update order type (admin only)"""
        order_data = self.database.update_document(
            database_id=self.database_id,
            collection_id='orders',
            document_id=order_id,
            data={
                'type': order_type.value
            }
        )
        return Order.from_dict(order_data)
    
    def get_order_info(self, order_id: str) -> Optional[Order]:
        """Get order details by ID"""
        try:
            order_data = self.database.get_document(
                database_id=self.database_id,
                collection_id='orders',
                document_id=order_id
            )
            items_result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='order_items',
                queries=[Query.equal('order_id', order_id)]
            )
            order_data['items'] = [OrderItem.from_dict(item) for item in items_result['documents']]
            return Order.from_dict(order_data)
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            return None
        
    def delete_order(self, order_id: str) -> bool:
        """Delete an order by ID"""
        try:
            # First delete all items associated with this order
            items_result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='order_items',
                queries=[Query.equal('order_id', order_id)]
            )
            for item in items_result['documents']:
                self.database.delete_document(
                    database_id=self.database_id,
                    collection_id='order_items',
                    document_id=item['$id']
                )
            
            # Now delete the order itself
            self.database.delete_document(
                database_id=self.database_id,
                collection_id='orders',
                document_id=order_id
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete order {order_id}: {e}")
            return False