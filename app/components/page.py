from components.titled import CustomTitled
from components.navigation import BottomNav
from fasthtml.components import Div, Html, Script

def AppContainer(content: Div, active_button_index: int = None) -> Div:
    return CustomTitled('Dera Manager',
                Html(data_theme='cupcake'),
                content,
                BottomNav(active_button_index),
            )