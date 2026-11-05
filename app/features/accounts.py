"""APP-002: signup, login, a private dashboard and logout for Fix-It Desk.

HTML forms and JSON endpoints call the same prepared security helpers, so the
browser and the API follow one set of rules on the server.
"""

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app import security
from app.schemas import LoginInput, PublicUser, SignupInput

router = APIRouter()


def _page(request: Request, name: str, status_code: int = 200, **context):
    """Render a page with a CSRF token, keeping any new pre-login session cookie."""
    holder = Response()
    token = security.csrf_token(request, holder)
    response = request.app.state.templates.TemplateResponse(
        request=request,
        name=name,
        context={"csrf_token": token, **context},
        status_code=status_code,
    )
    if "set-cookie" in holder.headers:
        response.headers.append("set-cookie", holder.headers["set-cookie"])
    return response


def _validation_message(error: ValidationError) -> str:
    """Explain the rule without echoing the submitted values back."""
    fields = {str(item["loc"][0]) for item in error.errors() if item["loc"]}
    if "username" in fields:
        return "Use 3–32 letters, numbers, or underscores for your username."
    return "Use a password between 15 and 128 characters."


# ---------- JSON API ----------


@router.get("/api/csrf")
def api_csrf(request: Request, response: Response):
    """Start a pre-login session and hand a same-origin client its CSRF token."""
    return {"csrf_token": security.csrf_token(request, response)}


@router.post("/api/signup", status_code=201, response_model=PublicUser)
def api_signup(
    request: Request,
    credentials: SignupInput,
    x_csrf_token: str | None = Header(default=None),
):
    """Create a member account. The role is never accepted from the request."""
    security.require_csrf(request, x_csrf_token)
    security.limit_signup(request)
    return security.signup(
        request.app.state.settings, credentials.username, credentials.password
    )


@router.post("/api/login", response_model=PublicUser)
def api_login(
    request: Request,
    response: Response,
    credentials: LoginInput,
    x_csrf_token: str | None = Header(default=None),
):
    """Check the password and set an HttpOnly session cookie; no token in JSON."""
    security.require_csrf(request, x_csrf_token)
    return security.login(request, response, credentials.username, credentials.password)


@router.get("/api/me", response_model=PublicUser)
def api_me(user: dict = Depends(security.require_user)):
    """401 before login, the current public identity after login."""
    return user


@router.post("/api/logout")
def api_logout(
    request: Request,
    response: Response,
    x_csrf_token: str | None = Header(default=None),
):
    """Revoke the session on the server, not only in this browser."""
    security.require_csrf(request, x_csrf_token)
    security.logout(request, response)
    return {"detail": "Logged out."}


# ---------- HTML pages ----------


@router.get("/signup", include_in_schema=False)
def signup_form(request: Request):
    """Show the account form."""
    return _page(request, "signup.html")


@router.post("/signup", include_in_schema=False)
def signup_submit(
    request: Request,
    username: str = Form(default=""),
    password: str = Form(default=""),
    csrf_token: str = Form(default=""),
):
    """Create a member, then send the visitor to log in."""
    try:
        security.require_csrf(request, csrf_token)
        credentials = SignupInput(username=username, password=password)
    except HTTPException as error:
        return _page(request, "signup.html", error.status_code, error=error.detail)
    except ValidationError as error:
        return _page(request, "signup.html", 422, error=_validation_message(error))
    try:
        security.limit_signup(request)
        security.signup(
            request.app.state.settings, credentials.username, credentials.password
        )
    except HTTPException as error:
        return _page(
            request,
            "signup.html",
            error.status_code,
            error=error.detail,
            username=credentials.username,
        )
    return RedirectResponse("/login?created=1", status_code=303)


@router.get("/login", include_in_schema=False)
def login_form(request: Request, created: str = ""):
    """Show the login form, with a note right after signup."""
    return _page(request, "login.html", created=created == "1")


@router.post("/login", include_in_schema=False)
def login_submit(
    request: Request,
    username: str = Form(default=""),
    password: str = Form(default=""),
    csrf_token: str = Form(default=""),
):
    """Log in and open the member space; mistakes keep only the username."""
    try:
        security.require_csrf(request, csrf_token)
        credentials = LoginInput(username=username, password=password)
    except HTTPException as error:
        return _page(request, "login.html", error.status_code, error=error.detail)
    except ValidationError:
        return _page(
            request,
            "login.html",
            422,
            error="Enter your username and password.",
        )
    redirect = RedirectResponse("/dashboard", status_code=303)
    try:
        security.login(request, redirect, credentials.username, credentials.password)
    except HTTPException as error:
        return _page(
            request,
            "login.html",
            error.status_code,
            error=error.detail,
            username=credentials.username,
        )
    return redirect


@router.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):
    """Members only: anonymous visitors are sent to the login page."""
    user = security.authenticate(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    return _page(request, "dashboard.html", user=user)


@router.post("/logout", include_in_schema=False)
def logout_submit(request: Request, csrf_token: str = Form(default="")):
    """Revoke the session, then return to the homepage."""
    try:
        security.require_csrf(request, csrf_token)
    except HTTPException:
        return RedirectResponse("/dashboard", status_code=303)
    response = RedirectResponse("/", status_code=303)
    security.logout(request, response)
    return response
