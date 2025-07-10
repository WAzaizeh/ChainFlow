from fasthtml.common import *

def success_message(message: str, duration: int = 3000) -> Div:
    """Reusable success message component that auto-disappears"""
    return Div(
        id="success-message",
        cls="fixed top-4 left-1/2 transform -translate-x-1/2 bg-green-500 \
            text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-all \
            duration-300 ease-in-out",
        style="transform: translateX(-50%);",
        hx_swap_oob="true"  # Out-of-band swap to update anywhere on page
    )(
        message,
        Script(f"""
            // Auto-hide after {duration}ms
            setTimeout(() => {{
                const msg = document.getElementById('success-message');
                if (msg) {{
                    msg.style.opacity = '0';
                    msg.style.transform = 'translateX(-50%) translateY(-20px)';
                    setTimeout(() => {{
                        msg.remove();
                    }}, 300);
                }}
            }}, {duration});
        """)
    )

def success_message_placeholder() -> Div:
    """Placeholder for success message - will be replaced by HTMX"""
    return Div(id="success-message", style="display: none;")