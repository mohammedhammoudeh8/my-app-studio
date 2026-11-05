"""APP-003: member/admin permissions enforced on the server for Fix-It Desk.

Hiding the Admin link is only presentation. Every admin request checks the
user's current role in the database, so a typed URL or an old token cannot
bypass it. Roles change only through the trusted local command:
``python studio.py user role USERNAME --role admin``.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app import security
from app.database import connect

router = APIRouter()


def _accounts(request: Request) -> list[dict[str, str]]:
    """Read-only account list for the admin view; never includes hashes."""
    with connect(request.app.state.settings) as connection:
        rows = connection.execute(
            "SELECT username, role FROM users ORDER BY role, username"
        ).fetchall()
    return [{"username": row["username"], "role": row["role"]} for row in rows]


@router.get("/api/admin")
def api_admin(request: Request, user: dict = Depends(security.require_admin)):
    """Anonymous → 401, member → 403, admin → 200 (checked on every request)."""
    accounts = _accounts(request)
    return {
        "admin": user["username"],
        "accounts": len(accounts),
        "admins": sum(1 for account in accounts if account["role"] == "admin"),
    }


@router.get("/admin", include_in_schema=False)
def admin_page(request: Request):
    """Same rule as the API: log in first, then the current role must be admin."""
    user = security.authenticate(request)
    templates = request.app.state.templates
    if user is None:
        return RedirectResponse("/login", status_code=303)
    if user["role"] != "admin":
        return templates.TemplateResponse(
            request=request, name="admin_denied.html", context={}, status_code=403
        )
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"user": user, "accounts": _accounts(request)},
    )
