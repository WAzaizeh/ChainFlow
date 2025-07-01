from fasthtml.common import *
from models.order import Order, OrderStatus

def render_draft_order(draft_order: Order) -> Div:
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
    )

def render_start_order_tab(draft_order: Order | None = None) -> list[Div]:
    """Render the start order tab content"""
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
            self.render_admin_actions(order) if is_admin
            else A("View", href=f"/orders/{order.id}", cls="btn btn-sm")
        )
    )

def status_badge(status: OrderStatus) -> Span:
    """Render a status badge with appropriate color"""
    colors = {
        OrderStatus.DRAFT: "bg-gray-200 text-gray-800",
        OrderStatus.SUBMITTED: "bg-blue-200 text-blue-800",
        OrderStatus.PROCESSING: "bg-yellow-200 text-yellow-800",
        OrderStatus.COMPLETED: "bg-green-200 text-green-800",
        OrderStatus.CANCELLED: "bg-red-200 text-red-800"
    }
    return Span(
        status.value.title(),
        cls=f"px-2 py-1 rounded-full text-sm {colors[status]}"
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