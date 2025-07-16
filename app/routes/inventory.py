from core.app import rt
from fasthtml.common import *
from layout.pages import InventoryPage
from layout.inventory import (
    quantity_adjuster,
    search_result_item,
    unit_input_component,
    inventory_edit_view,
    inventory_table_view,
    inventory_add_item,
    render_items_table
)
from db.inventory_db import InventoryDatabase
from db.auth import AuthDatabase
from models.inventory import StorageLocation
from datetime import datetime
from components.success_message import success_message
from models.user import UserRole

db = InventoryDatabase()

@rt('/inventory')
async def inventory(session):
    """Main inventory page"""
    # Check if user is admin
    user_id = session.get("user", {}).get("id")
    is_admin = AuthDatabase().get_user_role(user_id) == UserRole.ADMIN if user_id else False
    return InventoryPage(is_admin=is_admin)

@rt('/inventory/tab/edit')
async def get_edit_tab():
    """Get edit tab content"""
    return inventory_edit_view()

@rt('/inventory/tab/view')
async def get_view_tab():
    """Get view tab content"""
    return inventory_table_view()

@rt('/inventory/tab/add')
async def get_add_tab():
    """Get add tab content"""
    return inventory_add_item()

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
    
    secondary_units = db.get_item_secondary_units(item_id)
    return quantity_adjuster(item, secondary_units)

@rt('/inventory/update/{item_id}', methods=['POST'])
async def update_inventory(req, session, item_id: str):
    """Update inventory quantity and storage location"""
    data = await req.form()
    quantity = float(data.get('quantity', 0))
    unit = data.get('unit', '')
    storage = data.get('storage', StorageLocation.KITCHEN.value)
    
    # Skip update if quantity is 0
    if quantity == 0:
        return "No quantity change specified", 400
    
    try:
        # Get the item to check primary unit
        item = db.get_item(item_id)
        if not item:
            return "Item not found", 404
        
        # Calculate primary unit change
        if unit == item.primary_unit:
            # Already in primary units
            primary_quantity_change = quantity
        else:
            # Convert from secondary unit to primary unit
            primary_quantity_change = db.convert_to_primary_unit(item_id, quantity, unit)
        
        # Update the database
        success = db.update_item_quantity(
            item_id=item_id,
            primary_quantity_change=primary_quantity_change,
            original_unit=unit,
            original_quantity=quantity,
            storage=storage,
            timestamp=datetime.now(),
            user_id=session["user"]["id"]
        )
        
        if success:
            # Return success message with item details
            updated_item = db.get_item(item_id)
            message = f"✓ {updated_item.name} updated! New quantity: {updated_item.quantity} {updated_item.primary_unit}"
            
            return Div(
                success_message(message),
                # Clear the form
                Script("""
                    document.getElementById('search-form').reset();
                    document.getElementById('search-list').innerHTML = '';
                    document.getElementById('item-form').innerHTML = '';
                """)
            )
        return "Failed to update inventory", 500
        
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        return f"Error: {str(e)}", 500
    
@rt('/inventory/add', methods=['POST'])
async def add_inventory_item(req):
    """Add a new inventory item"""
    data = await req.form()
    item_name = data.get('name', '').strip()
    quantity = float(data.get('quantity', 1))
    primary_unit = data.get('unit_name_0', '').strip()
    storage = data.get('storage', StorageLocation.KITCHEN.value)
    branch = AuthDatabase().get_user_branch(data.get('user_id', ''))
    
    if not item_name or not primary_unit:
        return "Name and primary unit are required", 400
    
    # Get secondary unit data if provided
    secondary_units = []
    secondary_unit_name = data.get('unit_name_1', '').strip()
    secondary_conversion = data.get('conversion_rate_1', '')
    
    if secondary_unit_name and secondary_conversion:
        try:
            conversion_rate = float(secondary_conversion)
            secondary_units.append({
                'name': secondary_unit_name,
                'conversion': conversion_rate
            })
        except ValueError:
            return "Invalid conversion rate", 400
    
    try:
        item_id = db.add_item_with_units(
            item_name=item_name,
            initial_quantity=quantity,
            primary_unit=primary_unit,
            storage=storage,
            additional_units=secondary_units
        )
        return Div(
                success_message(f"✓ '{item_name}' added successfully to {storage.replace('_', ' ').title()}!"),
                # Show success form and add another button
                Div(cls="text-center p-8")(
                    Div(cls="text-green-600 mb-4")(
                        H3("Item Added Successfully!", cls="text-xl font-medium")
                    ),
                    P(f"'{item_name}' has been added to {storage.replace('_', ' ').title()} inventory", 
                    cls="text-gray-600 mb-4"),
                    Button(
                        "Add Another Item",
                        hx_get="/inventory/tab/add",
                        hx_target="#add-content",
                        hx_swap="innerHTML",
                        cls="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
                    )
                )
            )
    except Exception as e:
        return f"Failed to add item: {str(e)}", 500

@rt('/inventory/unit-input/{tier}', methods=['GET'])
async def get_unit_input(tier: int):
    """Return HTML for a new unit input component"""
    return unit_input_component(tier)

@rt('/inventory/add-form')
async def get_add_form():
    """Get the add item form"""
    return inventory_add_item()

@rt('/inventory/filter-table', methods=['POST'])
async def filter_table_by_storage(req):
    """Filter table by storage location from form submission"""
    data = await req.form()
    storage_location = data.get('storage', StorageLocation.KITCHEN.value)
    
    # Validate storage location
    if storage_location not in [loc.value for loc in StorageLocation]:
        return "Invalid storage location", 400
    
    # Get items from database
    items = db.get_items_by_storage(storage_location)
    
    # Return the rendered table
    return render_items_table(items, storage_location)

@rt('/inventory/table/{storage_location}')
async def get_items_by_storage(storage_location: str):
    """Get items filtered by storage location (for initial load)"""
    # Validate storage location
    valid_locations = [loc.value for loc in StorageLocation]
    if storage_location not in valid_locations:
        return "Invalid storage location", 400
    
    # Get items from database
    items = db.get_items_by_storage(storage_location)
    
    # Return the rendered table
    return render_items_table(items, storage_location)