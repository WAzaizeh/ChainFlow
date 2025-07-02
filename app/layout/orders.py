from fasthtml.common import *
from models.order import Order, OrderStatus, OrderType
from models.inventory import InventoryItem
from components.icon import Icon
from components.dropdown import Dropdown
import json

def render_draft_order(draft_order: Order| None = None) -> Div:
    """Render the current draft order card"""
    return Div(
        cls="mb-8 p-4 border rounded-lg bg-white shadow-sm"
    )(
        Div(cls="flex justify-between items-center mb-4")(
            H2("Current Draft Order", cls="text-xl font-semibold"),
            Span(
                draft_order.id[:8], 
                cls="text-sm text-gray-500"
            )
        ),
        Div(cls="space-y-2")(
            P(
                f"Created: {draft_order.created_at.strftime('%Y-%m-%d %H:%M')}",
                cls="text-sm text-gray-600"
            ),
            P(
                f"Items: {len(draft_order.items)}",
                cls="text-sm text-gray-600"
            )
        ),
        Div(cls="mt-4 flex gap-2")(
            A(
                "Continue Order",
                href=f"/orders/{draft_order.id}",
                cls="btn btn-primary"
            ),
            Button(
                "Delete Draft",
                hx_delete=f"/orders/{draft_order.id}",
                hx_confirm="Are you sure you want to delete this draft order?",
                cls="btn btn-outline btn-error"
            )
        )
    ) if draft_order else Div(
        cls="p-4 bg-gray-100 rounded-lg text-center"
    )(
        P("No draft order found", cls="text-gray-600")
    )

def render_start_order_tab(draft_order: Order | None = None) -> list[Div]:
    """Render the start order tab content"""
    try:
        return [
            # Show current draft if exists
            render_draft_order(draft_order) if draft_order else None,
            
            # Search bar for items
            Div(
                id="order-search-container",
                cls="mb-6 relative"
            )(
                Form(
                    id="order-search-form",
                    hx_post="/orders/search-items",
                    hx_trigger="input changed delay:200ms",
                    hx_target="#order-search-list",
                    cls="relative border rounded-lg shadow-sm focus-within:ring-2 \
                        focus-within:ring-blue-500 focus-within:border-transparent"
                )(
                    Input(
                        id="order-search-input",
                        type="text",
                        name="query",
                        placeholder="Search items to order...",
                        cls="w-full p-3 border-b border-gray-200 rounded-t-lg \
                            focus:outline-none !mb-0"
                    ),
                    Div(
                        id="order-search-list",
                        cls="max-h-60 overflow-y-auto w-full"
                    )
                )
            ),
            
            # Selected items will be shown here
            Div(
                id="order-items-list",
                cls="space-y-4"
            ),
            
            # Submit order button
            Button(
                "Submit Order",
                type="button",
                hx_post="/orders/submit",
                hx_confirm="Are you sure you want to submit this order?",
                cls="w-full mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg \
                    hover:bg-blue-600"
            )
        ]
    except Exception as e:
        return [Div("Error loading draft order", cls="text-red-500")]

def render_orders_list(orders: list[Order] = [], is_admin: bool = False):
    """Render the view orders tab content"""
    return [
        Table(
            Thead(
                Tr(
                    Th("Order ID"),
                    Th("Status"),
                    Th("Type"),
                    Th("Created"),
                    Th("Items"),
                    Th("Actions")
                )
            ),
            Tbody(
                *[render_order_row(order, is_admin) for order in orders]
            ),
            cls="table-auto w-full"
        ) if orders else P("No orders found", cls="text-gray-500 italic")
    ]

def render_order_row(self, order: Order, is_admin: bool = False) -> Tr:
    """Render a single order row"""
    return Tr(
        Td(order.id[:8]),
        Td(self.status_badge(order.status)),
        Td(order.type.value.title()),
        Td(order.created_at.strftime("%Y-%m-%d %H:%M")),
        Td(str(len(order.items))),
        Td(
            render_admin_actions(order) if is_admin
            else A("View", href=f"/orders/{order.id}", cls="btn btn-sm")
        )
    )

def status_badge(status: OrderStatus) -> Span:
    """Render a status badge with DaisyUI classes"""
    colors = {
        OrderStatus.DRAFT: "badge-neutral text-neutral-content",
        OrderStatus.SUBMITTED: "badge-primary text-primary-content",
        OrderStatus.PROCESSING: "badge-warning text-warning-content",
        OrderStatus.COMPLETED: "badge-success text-success-content", 
        OrderStatus.CANCELLED: "badge-error text-error-content"
    }
    return Span(
        status.value.title(),
        cls=f"btn btn-ghost rounded-btn {colors[status]}"
    )

def render_admin_actions(order: Order) -> Div:
    """Render admin action buttons"""
    return Div(cls="flex gap-2")(
        A("View", href=f"/orders/{order.id}", cls="btn btn-sm"),
        Button(
            "Edit Type",
            hx_get=f"/orders/{order.id}/edit-type",
            hx_target="#modal-content",
            cls="btn btn-sm btn-outline"
        )
    )

def render_type_pill(order: Order) -> Div:
    """Render order type pill with dropdown for admins"""
    base_classes = "px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800"
    
    return Div(cls="relative")(
        Button(
            Span(order.type.value.title()),
            Icon(
                "chevron-down",
                cls="ml-1 text-xs opacity-70 transition-transform",
                id=f"type-arrow-{order.id}"
            ),
            cls=f"{base_classes} flex items-center cursor-pointer",
            onclick=f"toggleTypeDropdown('{order.id}')",  # Added click handler
            hx_get=f"/orders/{order.id}/type-selector",
            hx_target=f"#type-dropdown-{order.id}",
            hx_swap="innerHTML",
            hx_trigger="click"
        ),
        Div(
            id=f"type-dropdown-{order.id}",
            cls="absolute top-full left-0 mt-1 w-48 bg-white rounded-lg shadow-lg \
                hidden z-50"
        )
    )

def render_order_detail(order: Order) -> Div:
    """Render detailed view of a single order"""
    return Div(
        cls="bg-white min-h-[calc(100vh-8rem)] flex flex-col"
    )(
        # Header with ID and status pills
        Div(cls="navbar bg-base-300 rounded-t-box")(
            # Left side - Order ID
            Div(cls="flex-1 px-2")(
                H2(f"Order #{order.id[:8]}", cls="text-lg font-bold")
            ),
            # Right side - Status and Type
            Div(cls="flex flex-1 justify-end px-2")(
                Div(cls="flex items-center gap-2")(
                    # Status Badge
                    status_badge(order.status),
                    # Type Dropdown
                    Dropdown(
                        value=order.type.value,
                        options=[(t.value, t.value.title()) for t in OrderType],
                        name="type",
                        on_change=f"/orders/{order.id}/type",
                        cls="dropdown-end",
                        id=f"type-dropdown-container-{order.id}",
                    )
                )
            )
        ),
        
        # Items section
        Div(cls="flex-grow p-6")(
            H3("Items", cls="text-xl font-semibold"),
            Table(
                Thead(
                    Tr(
                        Th("Item"),
                        Th("Quantity"),
                        Th("Notes"),
                        Th("")  # Actions column
                    )
                ),
                Tbody(
                    *[
                        Tr(
                            Td(item.product_id),
                            Td(str(item.quantity)),
                            Td(item.notes or "-"),
                            Td(
                                Button(
                                    "Remove",
                                    hx_delete=f"/orders/{order.id}/items/{item.id}",
                                    hx_confirm="Remove this item?",
                                    cls="text-red-600 hover:text-red-800"
                                ) if order.status == OrderStatus.DRAFT else None
                            )
                        ) for item in order.items
                    ],
                    id="items-tbody"
                ),
                cls="w-full"
            ) if order.items else P("No items added yet", cls="text-gray-500 italic"),
            
            # Add item search (only for draft orders)
            *([] if order.status != OrderStatus.DRAFT else [
                Div(cls="mt-6 pt-6 border-t")(
                    Form(
                        id="add-item-form",
                        hx_post=f"/orders/{order.id}/items",
                        hx_target="#items-tbody",
                        hx_swap="beforeend"
                    )(
                        Input(
                            type="text",
                            name="search",
                            placeholder="Search items to add...",
                            cls="w-full p-3 border rounded-lg focus:ring-2 \
                                focus:ring-blue-500 focus:border-transparent"
                        )
                    )
                )
            ])
        ),

        # Action buttons at bottom
        Div(cls="flex-none mt-auto pt-6 space-y-6")(
            # Action buttons
            Div(cls="flex justify-between w-full")(
                *([] if order.status != OrderStatus.DRAFT else [
                    Button(
                        "Delete Order", 
                        hx_delete=f"/orders/{order.id}",
                        hx_confirm="Are you sure you want to delete this order?",
                        cls="btn btn-outline"
                    ),
                    Button(
                        "Submit Order",
                        hx_post=f"/orders/{order.id}/submit",
                        hx_confirm="Are you sure you want to submit this order?",
                        cls="btn btn-primary"
                    )
                ])
            ),
            
            # Order metadata with top border
            Div(cls="border-t pt-4 text-sm text-gray-600 space-y-1")(
                P(f"Created by: {order.created_by}"),
                P(f"Created at: {order.created_at.strftime('%Y-%m-%d %H:%M')}"),
                P(f"Submitted at: {order.submitted_at.strftime('%Y-%m-%d %H:%M') if order.submitted_at else 'N/A'}")
            )
        )
    )

def render_search_result_item(item: InventoryItem) -> Div:
    """Render a single inventory item search result"""
    return Div(
        cls="p-4 hover:bg-gray-50 cursor-pointer"
    )(
        # Item details
        Div(cls="flex items-center justify-between")(
            # Left side - Name and quantity
            Div(cls="flex-1")(
                H4(item.name, cls="font-medium"),
                P(
                    f"Available: {item.quantity} {item.units[0] if item.units else ''}",
                    cls="text-sm text-gray-600"
                )
            ),
            # Right side - Add button
            Button(
                "Add",
                cls="btn btn-sm btn-primary",
                hx_post=f"/orders/draft/items",  # We'll create this route later
                hx_vals=json.dumps({
                    "product_id": item.id,
                    "quantity": 1
                }),
                hx_target="#order-items-list",
                hx_swap="beforeend"
            )
        )
    )