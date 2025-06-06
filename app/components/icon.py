from fasthtml.components import I

def Icon(name : str, solid : bool = True, **kwargs) -> I:
    custom_cls = kwargs.pop('cls', '')
    return I(cls=f"{'fas' if solid else 'far'} fa-{name} {custom_cls}", **kwargs)

def BrandIcon(name : str, **kwargs) -> I:
    custom_cls = kwargs.pop('cls', '')
    return I(cls=f'fab fa-{name} {custom_cls}', **kwargs)