from fasthtml.common import *
from appwrite.services.account import Account

from core.app import rt

@rt("/login", methods=["GET"])
def login_get(req):
    failed = req.query_params.get("failed")
    err = P("Google sign‑in failed, try again.", cls="text-red-600") if failed else ""
    return Titled(
        "Sign in",
        err,
        Form(method="post", cls="container flex flex-col gap-3")(
            Fieldset(
                Label("Email", Input(name="email", type="email", required=True)),
                Label("Password", Input(name="password", type="password", required=True)),
            ),
            Button("Login", type="submit"),
        ),
        Hr(),
        A("Continue with Google", href="/login/google", cls="btn btn-outline w-full"),
    )

@rt("/login/google", methods=["POST"])
async def login_post(req, session, account: Account):
    form = await req.form()
    try:
        sess = account.create_email_password_session(
            email=form["email"],
            password=form["password"]
        )
        session["user"] = {"id": sess["userId"], "email": form["email"]}
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        return Titled("Login failed", P(str(e)), A("Back", href="/login"))
    
