from fasthtml.common import *
from models.inventory import InventoryItem

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

def quantity_adjuster(item: InventoryItem = None) -> Form:
    """Quantity adjuster with +/- buttons and unit selector"""
    if not item:
        return Div()  # Return empty div if no item selected
        
    return Form(
        id="quantity-form",
        hx_post=f"/inventory/update/{item.id}",
        hx_swap="none",
        hx_trigger="submit",
        hx_indicator="#submit-indicator",
        hx_target="this",
        hx_on="""htmx:afterRequest: if(event.detail.successful) { 
               document.getElementById('success-message').classList.add('show');
               document.getElementById('search-form').reset();
               document.getElementById('search-results').innerHTML = '';
               document.getElementById('item-form').innerHTML = '';
               setTimeout(() => {
                   document.getElementById('success-message').classList.remove('show');
               }, 2000);
           }""",
        cls="space-y-4"
    )(
        # Item name display
        H3(item.name, cls="text-lg font-medium"),
        # Quantity adjuster
        Div(cls="flex items-center justify-center gap-2")(
            Button(
                "−",
                type="button",
                onclick="decrementQuantity()",
                cls="w-10 h-10 rounded-full bg-gray-200 font-bold"
            ),
            Input(
                type="number",
                id="quantity",
                name="quantity",
                value="1",
                min="1",
                cls="w-20 text-center border rounded-lg"
            ),
            Button(
                "+",
                type="button",
                onclick="incrementQuantity()",
                cls="w-10 h-10 rounded-full bg-gray-200 font-bold"
            )
        ),
        # Unit selector if applicable
        Div(cls="flex justify-center")(
            Select(
                name="unit",
                cls="border rounded-lg px-3 py-2"
            )(
                Option(value=unit, selected=not item.units)(unit) for unit in item.units
            )
        ),
        # Add loading indicator
        Div(
            id="submit-indicator",
            cls="htmx-indicator"
        )("Updating..."),
        # Submit button
        Button(
            type="submit",
            cls="w-full mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg \
                hover:bg-blue-600"
        )("Update Inventory")
    )

def inventory_table_view(items: list[InventoryItem]) -> Div:
    """Render inventory items in a responsive table/card view"""
    return Div(
        # Desktop Table View (hidden on mobile)
        Div(cls="hidden md:block overflow-x-auto")(
            Table(cls="table table-pin-rows table-pin-cols w-full")(
                Thead(
                    Tr(
                        Th("Item Name"),
                        Th("Quantity"),
                        Th("Unit"),
                        Th("Last Updated")
                    )
                ),
                Tbody(
                    *(
                        Tr(
                            Td(item.name),
                            Td(str(item.quantity)),
                            Td(item.units or "-"),
                            Td(item.last_updated.strftime("%Y-%m-%d %H:%M") if item.last_updated else "-")
                        ) for item in items
                    )
                )
            )
        ),
        # Mobile Card View (hidden on desktop)
        Div(cls="grid grid-cols-1 gap-4 md:hidden")(
            *(
                Div(cls="bg-white rounded-lg shadow p-4 space-y-2")(
                    Div(cls="font-medium text-lg text-gray-900")(item.name),
                    Div(cls="grid grid-cols-2 gap-2 text-sm")(
                        Div(cls="text-gray-500")("Quantity:"),
                        Div(cls="text-gray-900")(str(item.quantity)),
                        Div(cls="text-gray-500")("Unit:"),
                        Div(cls="text-gray-900")(item.units or "-"),
                        Div(cls="text-gray-500")("Last Updated:"),
                        Div(cls="text-gray-900")(
                            item.last_updated.strftime("%Y-%m-%d %H:%M") if item.last_updated else "-"
                        )
                    )
                ) for item in items
            )
        )
    )

def inventory_edit_view() -> Div:
    """Container for inventory edit form"""
    return Div(cls="p-4")(
        inventory_search_bar(),
        Div(id="item-form", cls="mt-6")
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
    """Form to add a new inventory item"""
    return Form(
        id="add-item-form",
        hx_post="/inventory/add",
        hx_swap="innerHTML",
        hx_target="#item-form",
        hx_on="htmx:afterRequest: if(event.detail.successful) { \
            document.getElementById('success-message').classList.add('show'); \
            setTimeout(() => { document.getElementById('success-message').classList.remove('show'); }, 2000); \
        }",
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
        Input(
            type="number", 
            name="quantity", 
            placeholder="Quantity", 
            min="1", 
            value="1", 
            required=True, 
            cls="w-full p-3 border rounded-lg"
        ),
        Div(cls="space-y-4")(
            unit_input_component(tier=0)
        ),
        Button(
            type="submit",
            cls="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600"
        )("Add Item")
    )