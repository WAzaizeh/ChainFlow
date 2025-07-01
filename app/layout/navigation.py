from datetime import datetime, time
from typing import List, Tuple, Optional
from fasthtml.common import *
from models.user import UserRole
from db.auth import AuthDatabase

class NavigationButton:
    def __init__(self, label: str, href: str, time_window: Optional[Tuple[time, time]] = None):
        self.label = label
        self.href = href
        self.time_window = time_window

    def is_enabled(self) -> bool:
        if not self.time_window:
            return True
        current_time = datetime.now().time()
        start, end = self.time_window
        if start <= end:
            return start <= current_time <= end
        return current_time >= start or current_time <= end

    def render(self) -> Div:
        enabled = self.is_enabled()
        return Div(
            cls="relative group"
        )(
            A(
                self.label,
                href=self.href if enabled else None,
                cls=f"w-full p-6 rounded-lg shadow-sm flex items-center justify-center \
                    text-lg font-medium {
                    'bg-white hover:bg-gray-50' if enabled 
                    else 'bg-gray-100 cursor-not-allowed text-gray-400'
                } transition-colors duration-150"
            ),
            *([
                Span(
                    f"Available {self.time_window[0].strftime('%I:%M %p')} - \
                      {self.time_window[1].strftime('%I:%M %p')}",
                    cls="absolute -top-8 left-1/2 transform -translate-x-1/2 \
                        bg-gray-800 text-white px-2 py-1 rounded text-sm \
                        opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                )
            ] if not enabled and self.time_window else [])
        )

def get_navigation_buttons(user_role: UserRole) -> List[NavigationButton]:
    """Get navigation buttons based on user role"""
    buttons = []
    
    # Common buttons
    if user_role in [UserRole.MEMBER, UserRole.ADMIN]:
        buttons.extend([
            NavigationButton("Edit Inventory", "/inventory"),
            NavigationButton("Closing Tasks", "/tasks", 
                           (time(20, 0), time(2, 0))),
            NavigationButton("Review Tasks", "/tasks", 
                           (time(2, 0), time(20, 0)))
        ])
    
    # Franchisee buttons
    if user_role == UserRole.FRANCHISEE:
        buttons.extend([
            NavigationButton("Start Order", "/orders"),
            NavigationButton("View Orders", "/orders/view")
        ])
    
    # Admin-specific buttons
    if user_role == UserRole.ADMIN:
        buttons.extend([
            NavigationButton("View Orders", "/orders/view"),
            NavigationButton("Manage Users", "/admin/users")
        ])
    
    return buttons

def render_main_navigation(user_role: UserRole) -> Div:
    """Render main navigation buttons"""
    buttons = get_navigation_buttons(user_role)
    return Div(cls="space-y-4")(
        *[button.render() for button in buttons]
    )