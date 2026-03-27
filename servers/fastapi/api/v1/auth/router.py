import re

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from api.dependencies.auth import require_authenticated_user
from utils.auth_backend import (
    JWT_COOKIE_NAME,
    create_access_token,
    make_session_id,
    should_use_secure_cookie,
    verify_admin_credentials,
)

API_V1_AUTH_ROUTER = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class SessionUserResponse(BaseModel):
    email: str
    displayName: str
    sessionId: str


EMAIL_REGEX = re.compile(
    r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$",
    re.IGNORECASE,
)


@API_V1_AUTH_ROUTER.post("/login", response_model=SessionUserResponse)
async def login(request: LoginRequest, response: Response):
    if not EMAIL_REGEX.match(request.email.strip()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")

    is_valid = verify_admin_credentials(request.email, request.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(request.email)
    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=should_use_secure_cookie(),
        samesite="lax",
        max_age=60 * 60 * 12,
        path="/",
    )

    normalized_email = request.email.strip().lower()
    return SessionUserResponse(
        email=normalized_email,
        displayName="Admin",
        sessionId=make_session_id(normalized_email),
    )


@API_V1_AUTH_ROUTER.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=JWT_COOKIE_NAME, path="/")
    return {"ok": True}


@API_V1_AUTH_ROUTER.get("/me", response_model=SessionUserResponse)
async def me(user=Depends(require_authenticated_user)):
    return SessionUserResponse(
        email=user["email"],
        displayName=user["displayName"],
        sessionId=user["sessionId"],
    )
