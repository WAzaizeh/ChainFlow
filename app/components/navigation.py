from components.icon import Icon
from fasthtml.components import A,Div, Button, Span, H1

def BottomNav(active_button_index: int = None) -> Div:
    return Div(
        A(Span('home', cls='material-symbols-rounded'), 'Home', cls=f"nav-item {'active' if active_button_index==1 else ''}", href='/'),
        A(Span('task', cls='material-symbols-rounded'), 'Tasks', cls=f"nav-item {'active' if active_button_index==2 else ''}", href='/tasks'),
        A(Span('inventory', cls='material-symbols-rounded'), 'Inventory', cls=f"nav-item {'active' if active_button_index==3 else ''}", href='/inventory'),
        A(Span('person', cls='material-symbols-rounded'), 'Profile', cls=f"nav-item {'active' if active_button_index==4 else ''}", href='/profile'),
        cls='btm-nav'
    )

def BackButton(**kwargs) -> Button:
    cls = 'btn btn-ghost' + kwargs.get('cls', '')
    return Button(
        Icon('chevron-left'),
        cls=cls,
        onclick='goBack()',
        **kwargs
        )

def TopNav(title: int = None) -> Div:
    return  Div(
                BackButton(),
                H1(
                    title,
                    onclick='goBack()',
                    cls='flex-1 text-black text-center top-nav-title text-2xl font-bold'
                    ),
                cls='flex justify-center items-center p-4 top-nav',
            ),