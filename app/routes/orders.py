from core.app import rt
from fasthtml.common import *
from db.order_db import OrderDatabase
from layout.pages import OrdersPage
from db.auth import AuthDatabase
from layout.pages import AppContainer
from layout.orders import (
    render_order_detail,
    render_search_result_item
)
from models.order import OrderStatus, OrderType
import logging
import json
from components.dropdown import Dropdown
from components.icon import Icon
from db.inventory_db import InventoryDatabase

logger = logging.getLogger(__name__)
db = OrderDatabase()
inventory_db = InventoryDatabase()

@rt('/orders/search-items', methods=['POST'])
async def search_inventory_items(request, session):
    """Search inventory items for adding to order"""
    # Check authentication - use same pattern as other routes
    if not session.get('user'):
        return RedirectResponse('/login', status_code=303)
    
    try:
        form = await request.form()
        query = form.get('query', '').strip()
        
        if len(query) < 2:
            return ""  # Return empty for short queries
            
        items = inventory_db.search_items(query)
        
        if not items:
            return Div(
                "No items found",
                cls="p-4 text-center text-gray-500"
            )
            
        return Div(cls="divide-y divide-gray-200")(
            *[render_search_result_item(item) for item in items]
        )
        
    except Exception as e:
        logger.error(f"Error searching items: {e}")
        return Response("Error searching items", status_code=500)

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

@rt('/orders/{order_id}/type', methods=['POST'])
async def update_order_type(order_id: str, type: str = Form(...)):
    """Update order type"""
    try:
        # Update order type
        new_type = OrderType(type)
        updated = db.update_order_type(order_id, new_type)
        
        if not updated:
            return Response("Failed to update order type", status_code=500)
        
        # Return updated dropdown
        return Dropdown(
            value=updated.type.value,
            options=[(t.value, t.value.title()) for t in OrderType],
            name="type",
            on_change=f"/orders/{order_id}/type",
            cls="dropdown-end",
            id=f"type-dropdown-{order_id}",
            disabled=False
        )
        
    except Exception as e:
        logger.error(f"Error updating order type: {e}")
        return Response(str(e), status_code=500)

@rt('/orders/{order_id}/type-selector')
async def type_selector(order_id: str):
    """Render order type selector dropdown menu"""
    order = db.get_order_info(order_id)
    if not order:
        return Response(status_code=404)
    
    return Ul(cls="p-0")(
        *[
            Li(
                A(
                    Div(cls="flex items-center justify-between")(
                        Span(type.value.title()),
                        Icon(
                            "check",
                            cls=f"{'visible' if order.type == type else 'invisible'} \
                                w-4 h-4"
                        )
                    ),
                    hx_post=f"/orders/{order_id}/type",
                    hx_vals=json.dumps({"type": type.value}),
                    cls="hover:bg-base-200"
                )
            ) for type in OrderType
        ]
    )

@rt('/orders/{order_id}')
async def view_order(order_id: str, session):
    """View or continue a draft order"""
    # Verify user has access to this order
    auth_db = AuthDatabase()
    user_branch = auth_db.get_user_branch(session)
    
    order = db.get_order_info(order_id)
    if not order or order.branch_id != user_branch:
        return RedirectResponse('/orders', status_code=303)
    
    return AppContainer(
        Div(cls="container mx-auto p-4 max-w-4xl")(
            # Back button
            A(
                "← Back to Orders",
                href="/orders",
                cls="text-blue-500 hover:underline mb-4 inline-block"
            ),
            
            # Order detail view
            render_order_detail(order)
        )
    )

@rt('/orders/{order_id}', methods=['DELETE'])
async def delete_draft(order_id: str, session):
    """Delete a draft order"""
    try:
        # Verify user has access to this order
        auth_db = AuthDatabase()
        user_branch = auth_db.get_user_branch(session)
        
        order = db.get_order_info(order_id)
        if not order or order.branch_id != user_branch:
            return Response(status_code=403)
            
        if order.status != OrderStatus.DRAFT:
            return Response("Only draft orders can be deleted", status_code=400)
            
        success = db.delete_order(order_id)
        if success:
            logger.info(f"Deleted draft order {order_id}")
            return Response(status_code=200)
        else:
            return Response("Failed to delete order", status_code=500)
            
    except Exception as e:
        logger.error(f"Error deleting draft order {order_id}: {e}")
        return Response(str(e), status_code=500)

@rt('/orders')
async def orders_page(session):
    """Render the orders page with all branch orders and draft order if exists"""
    if not session.get('user'):
        return RedirectResponse('/login', status_code=303)
    
    auth_db = AuthDatabase()
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