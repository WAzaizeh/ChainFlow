from core.app import rt
from fasthtml.common import *
from layout.pages import InventoryPage
from layout.inventory import quantity_adjuster, search_result_item
from db.inventory_db import InventoryDatabase
from datetime import datetime

db = InventoryDatabase()

@rt('/inventory')
async def inventory():
    """Main inventory page"""
    # Get all inventory items for table view
    items = db.get_all_items()
    return InventoryPage(items)

@rt('/inventory/search', methods=['POST'])
async def search_items(req):
    """Search items by name"""
    data = await req.form()
    query = data.get('query', '').strip()
    if len(query) < 2:
        return ""
    
    items = db.search_items(query)
    return Div(cls="bg-white rounded-b-lg")(
        *(search_result_item(item) for item in items)
    )

@rt('/inventory/select/{item_id}')
async def select_item(item_id: str):
    """Get item form when selected"""
    item = db.get_item(item_id)
    if not item:
        return "Item not found", 404
    return quantity_adjuster(item)

@rt('/inventory/update/{item_id}', methods=['POST'])
async def update_inventory(req, session, item_id: str):
    """Update inventory quantity"""
    data = await req.form()
    quantity = int(data.get('quantity', 1))
    unit = data.get('unit', '')
    
    success = db.update_item_quantity(
        item_id=item_id,
        quantity=quantity,
        unit=unit,
        timestamp=datetime.now().isoformat(),
        user_id=session["user"]["id"]
    )
    
    if success:
        return "Success"
    return "Failed to update inventory", 500