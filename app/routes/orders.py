from core.app import rt
from fasthtml.common import *
from db.order_db import OrderDatabase
from layout.pages import OrdersPage
from db.auth import AuthDatabase
import logging

logger = logging.getLogger(__name__)
db = OrderDatabase()

@rt('/orders')
async def orders_page(session):
    """Render the orders page with all branch orders and draft order if exists"""
    auth_db = AuthDatabase()
    if not session.get('user'):
        return RedirectResponse('/login', status_code=303)
    user_id = session['user']['id']
    user_is_admin = auth_db.is_admin(user_id)
    branch_id = auth_db.get_user_branch(session)
    
    orders = db.get_branch_orders(branch_id)
    draft_order = None if user_is_admin else db.get_draft_order(branch_id)
    
    return OrdersPage(
        orders=orders,
        draft_order=draft_order,
        is_admin=user_is_admin
    )

@rt('/orders/start', methods=['POST'])
async def start_order(session):
    """Start a new order draft for the user's branch"""
    if not session.get('user'):
        return RedirectResponse('/login', status_code=303)
    
    auth_db = AuthDatabase()
    branch_id = auth_db.get_user_branch(session)
    user_id = session['user']['id']
    
    # Check if draft already exists
    if db.get_draft_order(branch_id):
        return RedirectResponse('/orders', status_code=303)
        
    order = db.create_order(branch_id, user_id)
    return RedirectResponse(f'/orders/{order.id}', status_code=303)