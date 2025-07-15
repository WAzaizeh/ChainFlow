from fasthtml.common import *
from dotenv import load_dotenv
from core.static import fetch_static_files

# Load environment variables
load_dotenv()

# Headers setup
headers = (
    Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
    Script(src='https://unpkg.com/tailwindcss-cdn@3.4.3/tailwindcss.js'),
    Link(
        rel='stylesheet',
        href='https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css',),
    Script(src='https://cdn.tailwindcss.com'),
    Link(
        rel='stylesheet',
        href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css', 
        integrity='sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==', 
        crossorigin='anonymous',
        referrerpolicy='no-referrer'
    ),
    Link(
        rel='stylesheet',
        href='https://fonts.cdnfonts.com/css/inter',
    ),
    Link(
        rel='stylesheet',
        href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200',
    ),
    *fetch_static_files(),
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
    Script(src="https://cdn.jsdelivr.net/npm/appwrite@17.0.0"),
)

# Auth middleware
def auth_before(req, sess):
    user = sess.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    req.scope["user"] = user

# Skip auth for these paths
skip_auth = [
    r"/login.*", 
    r"/static/.*", 
    r"/favicon.*", 
    r"/assets/.*", 
    r"/oauth.*", 
    r"/login/google", 
    r"/oauth-token"
]

beforeware = Beforeware(auth_before, skip=skip_auth)

# Create FastHTML app
app, rt = fast_app(before=beforeware, hdrs=headers)