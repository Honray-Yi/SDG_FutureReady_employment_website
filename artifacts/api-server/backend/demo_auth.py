"""Public shared-demo sign-in; not a production identity or authorization service."""
from collections import defaultdict, deque
from functools import lru_cache
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
from threading import RLock
import tempfile
import time

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

# Intentionally PUBLIC demo credentials. Never use this account for real data.
DEMO_EMAIL = "demo@futureready.example"
DEMO_PASSWORD = "FutureReadyDemo2026!"
ITERATIONS = 600_000
SESSION_SECONDS = 7200
COOKIE = "fr_demo_session"
USER_FILE = Path(__file__).resolve().parents[3] / ".cache/futureready/demo-auth/users.json"
router = APIRouter(prefix="/api/demo-auth", tags=["demo-auth"])


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)


def fail(status, code, message):
    raise HTTPException(status, detail={"code": code, "message": message}, headers={"Cache-Control": "no-store"})


def password_hash(password, salt, iterations=ITERATIONS):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), iterations).hex()


class DemoStore:
    def __init__(self, path=USER_FILE):
        self.lock = RLock()
        self.sessions = {}
        self.attempts = defaultdict(deque)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            salt = secrets.token_hex(16)
            data = {"version": 1, "users": [{
                "user_id": "shared-demo", "email": DEMO_EMAIL, "display_name": "Demo Explorer",
                "algorithm": "pbkdf2_sha256", "iterations": ITERATIONS, "salt": salt,
                "password_hash": password_hash(DEMO_PASSWORD, salt),
            }]}
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
                    temporary = Path(output.name)
                    os.chmod(temporary, 0o600)
                    json.dump(data, output)
                os.replace(temporary, path)
            finally:
                if temporary:
                    temporary.unlink(missing_ok=True)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.user = data["users"][0]
        if (data["version"] != 1 or self.user["email"] != DEMO_EMAIL
                or self.user["algorithm"] != "pbkdf2_sha256"
                or self.user["iterations"] != ITERATIONS
                or len(bytes.fromhex(self.user["salt"])) != 16
                or len(bytes.fromhex(self.user["password_hash"])) != 32):
            raise ValueError("Invalid demo user store.")
        os.chmod(path, 0o600)

    def public_user(self):
        return {key: self.user[key] for key in ("user_id", "email", "display_name")} | {"is_demo": True}

    def login(self, email, password, client, previous=None):
        with self.lock:
            now = time.monotonic()
            self._prune(now)
            attempts = self.attempts[client]
            while attempts and attempts[0] <= now - 300:
                attempts.popleft()
            if len(attempts) >= 8:
                fail(429, "auth_rate_limited", "Too many demo sign-in attempts. Please wait five minutes.")
            attempts.append(now)
            # Always do the same expensive comparison, even for an unknown email.
            candidate = password_hash(password, self.user["salt"], self.user["iterations"])
            valid = hmac.compare_digest(candidate, self.user["password_hash"])
            if not valid or email.strip().casefold() != self.user["email"]:
                fail(401, "auth_invalid", "Incorrect email or password.")
            token = secrets.token_urlsafe(32)
            if previous:
                self.sessions.pop(hashlib.sha256(previous.encode()).hexdigest(), None)
            if len(self.sessions) >= 1000:
                fail(429, "auth_capacity", "The demo is at capacity. Please try later.")
            self.sessions[hashlib.sha256(token.encode()).hexdigest()] = now + SESSION_SECONDS
            return token

    def _prune(self, now):
        self.sessions = {key: expiry for key, expiry in self.sessions.items() if expiry > now}
        for key in list(self.attempts):
            values = self.attempts[key]
            while values and values[0] <= now - 300:
                values.popleft()
            if not values:
                del self.attempts[key]

    def current(self, token):
        with self.lock:
            self._prune(time.monotonic())
            if not token or hashlib.sha256(token.encode()).hexdigest() not in self.sessions:
                fail(401, "auth_required", "Please sign in to the demo.")
            return self.public_user()

    def logout(self, token):
        with self.lock:
            if token:
                self.sessions.pop(hashlib.sha256(token.encode()).hexdigest(), None)

    def session(self, token):
        with self.lock:
            user = self.current(token)
            remaining = self.sessions[hashlib.sha256(token.encode()).hexdigest()] - time.monotonic()
            return {"user": user, "expires_in": max(0, int(remaining))}


@lru_cache(maxsize=1)
def store():
    try:
        return DemoStore()
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        fail(503, "auth_unavailable", "The demo account store is unavailable.")


def mutation_guard(request):
    if request.headers.get("x-demo-action") != "1" or request.headers.get("sec-fetch-site") == "cross-site":
        fail(403, "auth_origin", "Use this site's demo sign-in form.")


def secure_cookie(request):
    return request.url.scheme == "https" or request.headers.get("x-forwarded-proto", "").split(",")[0].strip() == "https"


@router.post("/login")
def login(body: LoginInput, request: Request, response: Response):
    mutation_guard(request)
    service = store()
    token = service.login(body.email, body.password, request.client.host if request.client else "unknown",
                          request.cookies.get(COOKIE))
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, path="/", httponly=True,
                        secure=secure_cookie(request), samesite="lax")
    return {"user": service.public_user(), "expires_in": SESSION_SECONDS}


@router.get("/me")
def me(request: Request, response: Response):
    if not request.cookies.get(COOKIE):
        fail(401, "auth_required", "Please sign in to the demo.")
    response.headers["Cache-Control"] = "no-store"
    return store().session(request.cookies.get(COOKIE))


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response):
    mutation_guard(request)
    if request.cookies.get(COOKIE):
        store().logout(request.cookies.get(COOKIE))
    response.delete_cookie(COOKIE, path="/", httponly=True, secure=secure_cookie(request), samesite="lax")
    response.headers["Cache-Control"] = "no-store"
