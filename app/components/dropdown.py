from fasthtml.common import *
from components.icon import Icon
from typing import List, Tuple, Optional
import json

def Dropdown(
    value: str,
    options: List[Tuple[str, str]],  # List of (value, label) tuples
    name: str,
    on_change: Optional[str] = None,
    disabled: bool = False,
    cls: str = "",
    id: Optional[str] = None
) -> Div:
    """
    Render a DaisyUI dropdown with checkmarks for selected value
    
    Args:
        value: Current selected value
        options: List of (value, label) tuples
        name: Input name for form submission
        on_change: Optional HTMX post URL for handling changes
        disabled: Whether dropdown is disabled
        cls: Additional classes
        id: Optional ID for the dropdown element
    """
    return Div(
        id=id,
        cls=f"dropdown {cls}"
        )(
        # Trigger button
        Label(
            tabindex="0" if not disabled else None,
            role="button",
            cls=f"btn btn-ghost rounded-btn {'btn-disabled' if disabled else ''}"
        )(
            # Show current selection
            Span([opt[1] for opt in options if opt[0] == value][0]),
            # Dropdown arrow
            Icon("chevron-down", cls="ml-2 w-4 h-4")
        ),
        # Dropdown menu
        Ul(
            tabindex="0",
            cls="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
        )(
            *[
                Li(
                    A(
                         Div(cls="w-full flex items-center")(
                            Span(label, cls="flex-grow"),
                            Icon(
                                "check",
                                cls=f"ml-auto w-4 h-4 {'visible' if val == value else 'invisible'}"
                            )
                        ),
                        type="button",
                        hx_post=on_change if on_change else None,
                        hx_vals=json.dumps({name: val}) if on_change else None,
                        hx_target=f"#{id}",
                        hx_swap="outerHTML"
                    )
                ) for val, label in options
            ]
        )
    )