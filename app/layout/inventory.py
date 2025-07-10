from fasthtml.common import *
from models.inventory import (
    InventoryItem,
    ItemUnit,
    StorageLocation
)
from typing import List
from components.success_message import success_message

from db.inventory_db import InventoryDatabase
inventory_db = InventoryDatabase()

def storage_location_selector(current_storage: str = None) -> Div:
    """Storage location button selector"""
    default_storage = current_storage or StorageLocation.KITCHEN.value
    return Div(cls="space-y-2")(
        Label("Storage Location:", cls="block text-sm font-medium text-gray-700"),
        Div(cls="flex gap-2 flex-wrap")(
            *(
                Button(
                    location.value.replace('_', ' ').title(),
                    type="button",
                    name="storage",
                    value=location.value,
                    onclick=f"selectStorage('{location.value}')",
                    cls=f"px-4 py-2 rounded-lg border transition-colors duration-200 " +
                        ("bg-blue-500 text-white border-blue-500" if default_storage == location.value
                         else "bg-white text-gray-700 border-gray-300 hover:bg-gray-50")
                ) for location in StorageLocation
            )
        ),
        Input(type="hidden", name="storage", id="selected-storage", value=current_storage or StorageLocation.WAREHOUSE.value)
    )

def inventory_search_bar() -> Div:
    """Search bar with live suggestions"""
    return Div(
        id="search-container",
        cls="mb-6 relative"
    )(
        Form(
            id="search-form",
            hx_post="/inventory/search",
            hx_trigger="input changed delay:200ms",
            hx_target="#search-list",
            cls="relative border rounded-lg shadow-sm focus-within:ring-2 \
                focus-within:ring-blue-500 focus-within:border-transparent"
        )(
            Input(
                id="search-input",
                type="text",
                name="query",
                placeholder="Search items...",
                cls="w-full p-3 border-b border-gray-200 rounded-t-lg \
                    focus:outline-none !mb-0"
            ),
            # Search results will be injected here
            Div(
                id="search-list",
                cls="max-h-60 overflow-y-auto w-full"
            )
        )
    )

def search_result_item(item: InventoryItem) -> Button:
    """Render a single search result item"""
    return Button(
        item.name,
        hx_post=f"/inventory/select/{item.id}",
        hx_target="#item-form",
        hx_swap="innerHTML",
        style="border: none",
        **{
            "data-item-name": item.name,
            "hx-on::before-request": f"""
                document.getElementById('search-input').value = '{item.name}';
                document.getElementById('search-list').innerHTML = '';
            """
        },
        cls="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors duration-150"
    )

def quantity_adjuster(item: InventoryItem, secondary_units: List[ItemUnit]) -> Form:
    """Quantity adjuster with proper unit handling and storage selection"""
    if not item:
        return Div()
        
    return Form(
        id="quantity-form",
        hx_post=f"/inventory/update/{item.id}",
        hx_swap="none",
        hx_trigger="submit",
        hx_indicator="#submit-indicator",
        cls="space-y-4"
    )(
        H3(f"{item.name}", cls="text-lg font-medium"),
        P(f"Current: {item.quantity} {item.primary_unit}", cls="text-sm text-gray-600"),

        # Quantity adjuster (allows negative values)
        Div(cls="space-y-2")(
            Label("Quantity Change:", cls="block text-sm font-medium text-gray-700"),
            Div(cls="flex items-center justify-center gap-2")(
                Button("−", type="button", onclick="decrementQuantity()", 
                       cls="w-10 h-10 rounded-full bg-gray-200 font-bold"),
                Input(type="number", id="quantity", name="quantity", value="0", 
                      step="0.01", cls="w-24 text-center border rounded-lg"),
                Button("+", type="button", onclick="incrementQuantity()", 
                       cls="w-10 h-10 rounded-full bg-gray-200 font-bold")
            ),
            P(cls="text-xs text-gray-500 text-center")(
                "Enter positive numbers to add, negative to subtract"
            )
        ),
        
         # Unit selector
        Div(cls="space-y-2")(
            Label("Unit:", cls="block text-sm font-medium text-gray-700"),
            Select(name="unit", cls="w-full border rounded-lg px-3 py-2")(
                Option(value=item.primary_unit, selected=True)(f"{item.primary_unit} (primary)"),
                *(Option(value=unit.unit_name)(
                    f"{unit.unit_name} (1 = {unit.conversion_to_primary} {item.primary_unit})"
                ) for unit in secondary_units)
            )
        ),
        
        Button(type="submit", cls="w-full mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600")(
            "Update Inventory"
        ),
    )

def inventory_edit_view() -> Div:
    """Container for inventory edit form"""
    return Div(cls="p-4")(
        storage_location_selector(),
        inventory_search_bar(),
        Div(id="item-form", cls="mt-6")
    )

def inventory_table_view() -> Div:
    """Enhanced table view with form-wrapped storage filtering"""
    return Div(
        id="table-view-container",
        cls="space-y-4"
    )(
        # Storage filter form
        Form(
            id="storage-filter-form",
            hx_post="/inventory/filter-table",
            hx_target="#table-content",
            hx_swap="innerHTML",
            hx_trigger="click from:button[name='storage']",
            cls="bg-gray-50 p-4 rounded-lg"
        )(
            storage_location_selector(StorageLocation.KITCHEN.value),  # Default to kitchen
            P(cls="text-xs text-gray-500 mt-2")(
                "Click a storage location to filter items"
            )
        ),
        
        # Table content container
        Div(
            id="table-content",
            hx_get="/inventory/table/kitchen",  # Load kitchen items by default
            hx_trigger="load",
            hx_swap="innerHTML"
        )(
            P("Loading items...", cls="text-center text-gray-500 p-4")
        ),
        
        # Keep the existing JavaScript for visual button states
        Script("""
            function selectStorage(storage) {
                // Remove active class from all buttons
                document.querySelectorAll('button[name="storage"]').forEach(btn => {
                    btn.className = btn.className.replace('bg-blue-500 text-white border-blue-500', 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50');
                });
                
                // Add active class to clicked button
                event.target.className = event.target.className.replace('bg-white text-gray-700 border-gray-300 hover:bg-gray-50', 'bg-blue-500 text-white border-blue-500');
                
                // Update hidden input
                document.getElementById('selected-storage').value = storage;
                
                // Trigger the form submission
                document.getElementById('storage-filter-form').dispatchEvent(new Event('change', { bubbles: true }));
            }
        """)
    )

def render_items_table(items: List[InventoryItem], storage_location: str) -> Div:
    """Render the actual items table"""
    if not items:
        return Div(cls="text-center p-8")(
            P(f"No items found in {storage_location.replace('_', ' ').title()} storage", 
              cls="text-gray-500"),
            P("Try selecting a different storage location or add some items", 
              cls="text-sm text-gray-400")
        )
    
    return Div(
        # Desktop Table View
        Div(cls="hidden md:block overflow-x-auto")(
            Table(cls="table table-pin-rows table-pin-cols w-full")(
                Thead(Tr(
                    Th("Item Name"), 
                    Th("Quantity"), 
                    Th("Branch"), 
                    Th("Storage"), 
                    Th("Last Updated")
                )),
                Tbody(
                    *(
                        Tr(
                            Td(item.name),
                            Td(f"{item.quantity} {item.primary_unit}"),
                            Td(item.branch),
                            Td(item.storage.replace('_', ' ').title()),
                            Td(item.last_updated if item.last_updated else "-")
                        ) for item in items
                    )
                )
            )
        ),
        # Mobile Card View
        Div(cls="grid grid-cols-1 gap-4 md:hidden")(
            *(
                Div(cls="bg-white rounded-lg shadow p-4 space-y-2")(
                    Div(cls="font-medium text-lg text-gray-900")(item.name),
                    Div(cls="grid grid-cols-2 gap-2 text-sm")(
                        Div(cls="text-gray-500")("Quantity:"),
                        Div(cls="text-gray-900")(f"{item.quantity} {item.primary_unit}"),
                        Div(cls="text-gray-500")("Branch:"),
                        Div(cls="text-gray-900")(item.branch),
                        Div(cls="text-gray-500")("Storage:"),
                        Div(cls="text-gray-900")(item.storage.replace('_', ' ').title()),
                        Div(cls="text-gray-500")("Last Updated:"),
                        Div(cls="text-gray-900")(
                            item.last_updated if item.last_updated else "-"
                        )
                    )
                ) for item in items
            )
        ),
        # Summary
        Div(cls="mt-4 p-3 bg-blue-50 rounded-lg")(
            P(f"Showing {len(items)} item{'s' if len(items) != 1 else ''} in {storage_location.replace('_', ' ').title()}", 
              cls="text-sm text-blue-700")
        )
    )

def unit_input_component(tier: int = 0) -> Div:
    """
    Reusable unit input component for primary (tier=0) and secondary (tier=1) units
    """
    if tier > 1:
        raise ValueError("Only primary and secondary tiers are supported")
    
    is_primary = tier == 0
    return Div(
        cls="unit-input-container space-y-4 !mt-0",
        **{"data-tier": str(tier)}
    )(
        # Unit name input
        Input(
            type="text",
            name=f"unit_name_{tier}",
            placeholder=f"{'Primary' if is_primary else 'Secondary'} unit name",
            cls="w-full p-3 border rounded-lg",
            required=True,  # Both primary and secondary are required
            **{"hx-on:input": "updateConversionLabel(this)" if not is_primary else None}
        ),
        # Conversion rate input (only for secondary unit)
        (
            Label(cls="block !mt-0")(
                Span(
                    cls="text-sm text-gray-600 conversion-label ml-2",
                    **{"data-primary-unit": "true"}
                )("How many units in one primary unit?"),
                Input(
                    type="number",
                    name=f"conversion_rate_{tier}",
                    min="0.000001",
                    step="any",
                    placeholder="Conversion rate",
                    required=True,  # Make conversion rate required
                    cls="w-full p-3 border rounded-lg mt-1"
                )
            )
        ) if not is_primary else "",
        # Add secondary unit button (only for primary unit)
        Button(
            hx_get="/inventory/unit-input/1",
            hx_target="this",
            hx_swap="outerHTML",
            type="button",
            cls="text-blue-500 hover:text-blue-600 pl-0 !mt-0",
            style="border: none"
        )("+ Add secondary unit") if is_primary else ""
    )

def inventory_add_item() -> Form:
    """Form to add a new inventory item with storage selection"""
    return Form(
        id="add-item-form",
        hx_post="/inventory/add",
        hx_swap="innerHTML",
        hx_target="#add-content",
        cls="space-y-4"
    )(
        H3("Add New Item", cls="text-lg font-medium"),
        Input(
            type="text", 
            name="name", 
            placeholder="Item Name", 
            required=True, 
            cls="w-full p-3 border rounded-lg"
        ),
        # Starting quantity input
        H4("Starting Quantity", cls="text-sm text-gray-600"),
        Input(
            type="number", 
            name="quantity", 
            placeholder="Quantity", 
            min="0.01",
            step="0.01", 
            value="1", 
            required=True, 
            cls="w-full p-3 border rounded-lg"
        ),
        Div(cls="space-y-4")(
            unit_input_component(tier=0)
        ),        
        # Storage location selector
        storage_location_selector(),

        Button(
            type="submit",
            cls="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600"
        )("Add Item"),
        
        Script("""
            function selectStorage(storage) {
                // Remove active class from all buttons
                document.querySelectorAll('button[name="storage"]').forEach(btn => {
                    btn.className = btn.className.replace('bg-blue-500 text-white border-blue-500', 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50');
                });
                
                // Add active class to clicked button
                event.target.className = event.target.className.replace('bg-white text-gray-700 border-gray-300 hover:bg-gray-50', 'bg-blue-500 text-white border-blue-500');
                
                // Update hidden input
                document.getElementById('selected-storage').value = storage;
            }
        """)
    )

def inventory_tabs(is_admin: bool = False) -> Div:
    """Render the inventory tabs with lazy loading"""
    return Div(cls="flex flex-col gap-2")(
        # Tabs
        Div(
            role="tablist",
            id="inventory-tabs",
            cls="tabs tabs-lifted"
        )(
            Input(
                type="radio",
                name="inventory_tab",
                role="tab",
                cls="tab",
                id="edit-tab",
                checked=True,
                aria_label="Edit",
                hx_trigger="change",
                hx_get="/inventory/tab/edit",
                hx_target="#edit-content"
            ),
            Div(
                role="tabpanel",
                cls="tab-content bg-base-100 border-base-300 rounded-box p-6",
                id="edit-content"
            )(
                # Load edit content immediately since it's the default tab
                inventory_edit_view()
            ),
            Input(
                type="radio",
                name="inventory_tab",
                role="tab",
                cls="tab",
                id="view-tab",
                aria_label="View",
                hx_trigger="change",
                hx_get="/inventory/tab/view",
                hx_target="#view-content"
            ),
            Div(
                role="tabpanel",
                cls="tab-content bg-base-100 border-base-300 rounded-box p-6",
                id="view-content"
            )(
                # Empty initially - will be loaded when tab is clicked
                P("Loading...", cls="text-center text-gray-500")
            ),
            *([] if not is_admin else [
                Input(
                    type="radio",
                    name="inventory_tab",
                    role="tab",
                    cls="tab",
                    id="add-tab",
                    aria_label="Add New",
                    hx_trigger="change",
                    hx_get="/inventory/tab/add",
                    hx_target="#add-content"
                ),
                Div(
                    role="tabpanel",
                    cls="tab-content bg-base-100 border-base-300 rounded-box p-6",
                    id="add-content"
                )(
                    # Empty initially - will be loaded when tab is clicked
                    P("Loading...", cls="text-center text-gray-500")
                ),
            ])
        ),
        Script("""
            function selectStorage(storage) {
                // Remove active class from all buttons
                document.querySelectorAll('button[name="storage"]').forEach(btn => {
                    btn.className = btn.className.replace('bg-blue-500 text-white border-blue-500', 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50');
                });
                
                // Add active class to clicked button
                event.target.className = event.target.className.replace('bg-white text-gray-700 border-gray-300 hover:bg-gray-50', 'bg-blue-500 text-white border-blue-500');
                
                // Update hidden input
                document.getElementById('selected-storage').value = storage;
            }
        """)
    )