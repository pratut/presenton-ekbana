import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from utils.get_env import get_app_data_directory_env, get_jwt_secret_env

ADMIN_EMAIL = "admin@ekbana.info"
DEFAULT_ADMIN_PASSWORD = "password"
AUTH_STORE_FILE = "admin_auth.json"

JWT_COOKIE_NAME = "ekbana_session"
JWT_EXP_SECONDS = 60 * 60 * 12


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _hash_password(password: str, *, salt_hex: str | None = None, rounds: int = 210000) -> str:
    salt = os.urandom(16) if salt_hex is None else bytes.fromhex(salt_hex)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return f"pbkdf2_sha256${rounds}${salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algo, rounds, salt_hex, hash_hex = stored_hash.split("$")
        if algo != "pbkdf2_sha256":
            return False
        computed = _hash_password(password, salt_hex=salt_hex, rounds=int(rounds))
        return hmac.compare_digest(computed, stored_hash)
    except ValueError:
        return False


def make_session_id(email: str) -> str:
    digest = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
    return f"u_{digest[:20]}"


def _get_auth_store_path() -> str:
    app_data_directory = get_app_data_directory_env() or "/app_data"
    os.makedirs(app_data_directory, exist_ok=True)
    return os.path.join(app_data_directory, AUTH_STORE_FILE)


def ensure_admin_auth_store_exists() -> None:
    auth_store_path = _get_auth_store_path()
    if os.path.exists(auth_store_path):
        return

    payload = {
        "email": ADMIN_EMAIL,
        "password_hash": _hash_password(DEFAULT_ADMIN_PASSWORD),
        "created_at": int(time.time()),
    }
    with open(auth_store_path, "w", encoding="utf-8") as file:
        json.dump(payload, file)


def _load_admin_auth_store() -> dict[str, Any]:
    ensure_admin_auth_store_exists()
    auth_store_path = _get_auth_store_path()
    with open(auth_store_path, "r", encoding="utf-8") as file:
        return json.load(file)


def verify_admin_credentials(email: str, password: str) -> bool:
    auth_store = _load_admin_auth_store()
    normalized_email = email.strip().lower()
    if normalized_email != auth_store.get("email", ADMIN_EMAIL).strip().lower():
        return False
    return verify_password(password, auth_store.get("password_hash", ""))


def create_access_token(email: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": email.strip().lower(),
        "email": email.strip().lower(),
        "session_id": make_session_id(email),
        "iat": now,
        "exp": now + JWT_EXP_SECONDS,
    }
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    secret = (get_jwt_secret_env() or "ekbana-dev-secret-change-me").encode("utf-8")
    signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid token format") from exc

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    secret = (get_jwt_secret_env() or "ekbana-dev-secret-change-me").encode("utf-8")
    expected_signature = _base64url_encode(hmac.new(secret, signing_input, hashlib.sha256).digest())
    if not hmac.compare_digest(expected_signature, encoded_signature):
        raise ValueError("Invalid token signature")

    payload_bytes = _base64url_decode(encoded_payload)
    payload = json.loads(payload_bytes.decode("utf-8"))
    now = int(time.time())
    if int(payload.get("exp", 0)) < now:
        raise ValueError("Token expired")
    return payload


def should_use_secure_cookie() -> bool:
    cookie_secure = os.getenv("AUTH_COOKIE_SECURE", "false").strip().lower()
    return cookie_secure in {"1", "true", "yes"}
