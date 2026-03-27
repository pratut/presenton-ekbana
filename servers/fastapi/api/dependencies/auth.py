from fastapi import Cookie, HTTPException, status

from utils.auth_backend import ADMIN_EMAIL, JWT_COOKIE_NAME, decode_access_token


def require_authenticated_user(
    session_token: str | None = Cookie(default=None, alias=JWT_COOKIE_NAME),
):
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(session_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    email = str(payload.get("email") or "").strip().lower()
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    return {
        "email": email,
        "displayName": "Admin",
        "sessionId": payload.get("session_id"),
    }
