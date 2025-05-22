from fasthtml.common import *
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Headers setup
headers = (
    Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
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