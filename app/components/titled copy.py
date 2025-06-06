from fastcore.meta import delegates
from fastcore.xml import FT
from fasthtml.components import Title, Main, H1, ft_hx

@delegates(ft_hx, keep=True)
def CustomTitled(title:str="FastHTML app", *args, cls="container", **kwargs)->FT:
    "An HTML partial containing a `Title`, and `H1`, and any provided children"
    return Title(title), Main(*args, cls=cls, **kwargs)