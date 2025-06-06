from pathlib import Path
from datetime import datetime
from fasthtml.common import Link, Script

def cache_busting():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def fetch_static_files() -> list:
    static_files = []
    for path in Path('./assets').rglob('*'):
        if path.is_file() and path.suffix == '.css':
            static_files.append(Link(rel='stylesheet', href=f'/{path.name}?t={cache_busting()}', type='text/css'))
        elif path.is_file() and path.suffix == '.js':
            static_files.append(Script(src=f'/{path.name}?t={cache_busting()}'))
    return static_files