# Auth Setup and Testing

This project now uses backend-verified login with an HTTP-only cookie session.

## Fixed Admin User

- Email: `admin@ekbana.info`
- Password: `password`

On first backend startup, a local auth file is created in app data:

- `/app_data/admin_auth.json` (inside container)
- `./app_data/admin_auth.json` (on host, via volume mount)

Only the hashed password is stored there.

## Required Environment Variables

Set these before running production:

- `JWT_SECRET` (required, long random value)
- `AUTH_COOKIE_SECURE=true` (recommended in HTTPS production)

For local HTTP development, use:

- `AUTH_COOKIE_SECURE=false`

## Docker Compose (Production)

```bash
cd /home/ek-lap-47/Ekbana/presenton-ekbana

export JWT_SECRET="replace-with-a-long-random-secret"
export AUTH_COOKIE_SECURE=false

docker compose up -d production --build
```

Open app:

- `http://localhost:5068`

## Docker Compose (Development)

```bash
cd /home/ek-lap-47/Ekbana/presenton-ekbana

export JWT_SECRET="replace-with-a-long-random-secret"
export AUTH_COOKIE_SECURE=false

docker compose up -d development --build
```

Open app:

- `http://localhost:5000`

## API Smoke Tests (curl)

Use a cookie jar file to preserve the session cookie.

### 1) Login

```bash
curl -i -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ekbana.info","password":"password"}' \
  http://localhost:5068/api/v1/auth/login
```

Expected: `200 OK` and `Set-Cookie: ekbana_session=...; HttpOnly`

### 2) Get Current User

```bash
curl -i -b cookies.txt \
  http://localhost:5068/api/v1/auth/me
```

Expected: `200 OK` with user payload.

### 3) Logout

```bash
curl -i -X POST -b cookies.txt -c cookies.txt \
  http://localhost:5068/api/v1/auth/logout
```

Expected: `200 OK` and cookie cleared.

### 4) Protected Endpoint Check (after logout)

```bash
curl -i -b cookies.txt \
  http://localhost:5068/api/v1/ppt/openai/models/available
```

Expected: `401 Unauthorized` (or method-specific error if not authenticated and endpoint requires auth).

## Frontend Behavior

- Unauthenticated users are redirected to `/login`.
- Successful login sets backend session cookie.
- Refresh keeps session while cookie is valid.
- Logout clears backend cookie and frontend auth state.
