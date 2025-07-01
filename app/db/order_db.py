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
        order_data = self.database.create_document(
            database_id=self.database_id,
            collection_id='orders',
            document_id=ID.unique(),
            data={
                'branch_id': branch_id,
                'status': OrderStatus.DRAFT.value,
                'type': OrderType.REGULAR.value,
                'items': [],
                'created_by': user_id,
                'created_at': datetime.now().isoformat()
            }
        )
        return Order.from_dict(order_data)

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
                print(f"Order {doc['$id']} items: {doc['items']}")
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
        docs = result['documents']
        if docs:
            # fetch order items for the draft order
            items_result = self.database.list_documents(
                database_id=self.database_id,
                collection_id='order_items',
                queries=[Query.equal('order_id', docs[0]['$id'])]
            )
            docs[0]['items'] = [OrderItem.from_dict(item) for item in items_result['documents']]
        print(f"Draft Order {docs[0]['$id']} items: {docs[0]['items']}")
        return Order.from_dict(docs[0]) if docs else None

    def add_item(self, order_id: str, product_id: str, quantity: int, notes: Optional[str] = None) -> OrderItem:
        """Add item to order"""
        item_data = self.database.create_document(
            database_id=self.database_id,
            collection_id='order_items',
            document_id=ID.unique(),
            data={
                'order_id': order_id,
                'product_id': product_id,
                'quantity': quantity,
                'notes': notes,
                'created_at': datetime.now().isoformat()
            }
        )
        return OrderItem.from_dict(item_data)

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