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
                Option(value="", selected=not item.unit)("No unit"),
                Option(value="kg", selected=item.unit == "kg")("Kilograms"),
                Option(value="g", selected=item.unit == "g")("Grams"),
                Option(value="l", selected=item.unit == "l")("Liters"),
                Option(value="ml", selected=item.unit == "ml")("Milliliters"),
                Option(value="pcs", selected=item.unit == "pcs")("Pieces")
            )
        ) if item.has_unit else "",
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
    """Render inventory items in a table view"""
    return Div(cls="overflow-x-auto")(
        Table(cls="table table-pin-rows table-pin-cols")(
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
                        Td(item.unit or "-"),
                        Td(item.last_updated.strftime("%Y-%m-%d %H:%M") if item.last_updated else "-")
                    ) for item in items
                )
            )
        )
    )

def inventory_edit_view() -> Div:
    """Container for inventory edit form"""
    return Div(cls="p-4")(
        inventory_search_bar(),
        Div(id="item-form", cls="mt-6")
    )