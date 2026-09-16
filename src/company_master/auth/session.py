"""Session management with HttpOnly cookies (DASH-01 S-2).

Security improvements:
- API keys stored in HttpOnly cookies instead of URL params/localStorage
- SameSite=Strict to prevent CSRF
- Secure flag for HTTPS
- Session TTL with automatic cleanup
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from company_master.auth.rbac import has_role

# Session configuration
SESSION_COOKIE_NAME = "huginn_session"
SESSION_TTL = 3600 * 24  # 24 hours
DASH_SECRET = os.getenv("DASH_SECRET", "change-me-in-production")

# In-memory session store (use Redis in production)
_sessions: dict[str, dict[str, Any]] = {}

# Rate limiting per IP
_rate_limits: dict[str, list[float]] = {}
_RATE_LIMIT_WINDOW = 60  # 1 minute
_RATE_LIMITS = {
    "anon": 30,
    "user": 60,
    "analyst": 120,
    "admin": 300,
}


class SessionUser(BaseModel):
    """User info stored in session."""
    user_id: str
    email: str
    role: str
    tier: str
    company_name: str | None = None
    credit_balance: int = 0


class SessionData(BaseModel):
    """Session data structure."""
    user: SessionUser | None = None
    created_at: float = 0
    last_activity: float = 0
    ip_address: str = ""


def _generate_session_id() -> str:
    """Generate a cryptographically secure session ID."""
    return secrets.token_urlsafe(32)


def _hash_session_id(session_id: str) -> str:
    """Hash session ID for storage (prevents timing attacks)."""
    return hashlib.sha256(session_id.encode()).hexdigest()


def create_session(
    user: SessionUser,
    ip_address: str,
    response: Response,
) -> str:
    """Create a new session with HttpOnly cookie.
    
    Args:
        user: User information
        ip_address: Client IP address
        response: FastAPI Response object to set cookie on
        
    Returns:
        Session ID (for API response)
    """
    session_id = _generate_session_id()
    session_hash = _hash_session_id(session_id)
    
    now = time.time()
    _sessions[session_hash] = {
        "user": user.model_dump(),
        "created_at": now,
        "last_activity": now,
        "ip_address": ip_address,
    }
    
    # Set HttpOnly cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=os.getenv("DASH_SECURE_COOKIES", "true").lower() == "true",
        samesite="strict",
        max_age=SESSION_TTL,
        path="/",
    )
    
    return session_id


def get_session(request: Request) -> SessionData | None:
    """Get session from HttpOnly cookie.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Session data if valid, None otherwise
    """
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        return None
    
    session_hash = _hash_session_id(session_id)
    session = _sessions.get(session_hash)
    
    if not session:
        return None
    
    # Check TTL
    now = time.time()
    if now - session["last_activity"] > SESSION_TTL:
        # Session expired
        del _sessions[session_hash]
        return None
    
    # Update last activity
    session["last_activity"] = now
    
    user_data = session.get("user")
    if user_data:
        return SessionData(
            user=SessionUser(**user_data),
            created_at=session["created_at"],
            last_activity=session["last_activity"],
            ip_address=session["ip_address"],
        )
    
    return None


def destroy_session(request: Request, response: Response) -> None:
    """Destroy session and clear cookie."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        session_hash = _hash_session_id(session_id)
        _sessions.pop(session_hash, None)
    
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


def check_rate_limit(ip_address: str, role: str = "anon") -> bool:
    """Check if request is within rate limit.
    
    Args:
        ip_address: Client IP
        role: User role for rate limit tier
        
    Returns:
        True if within limit, False if exceeded
    """
    limit = _RATE_LIMITS.get(role, _RATE_LIMITS["anon"])
    now = time.time()
    
    # Clean old entries
    if ip_address not in _rate_limits:
        _rate_limits[ip_address] = []
    
    _rate_limits[ip_address] = [
        t for t in _rate_limits[ip_address] 
        if now - t < _RATE_LIMIT_WINDOW
    ]
    
    if len(_rate_limits[ip_address]) >= limit:
        return False
    
    _rate_limits[ip_address].append(now)
    return True


def require_auth(request: Request) -> SessionData:
    """Dependency that requires valid session.
    
    Raises HTTPException(401) if not authenticated.
    """
    session = get_session(request)
    if not session or not session.user:
        raise HTTPException(
            status_code=401,
            detail="Oturum gecersiz. Lütfen giriş yapın."
        )
    return session


def require_role(required_role: str) -> Callable:
    """Factory for role-based dependency.
    
    Args:
        required_role: Minimum required role
        
    Returns:
        Dependency function
    """
    def dependency(request: Request) -> SessionData:
        session = get_session(request)
        if not session or not session.user:
            raise HTTPException(
                status_code=401,
                detail="Oturum gecersiz."
            )
        
        user_role = session.user.role
        if not has_role(user_role, required_role):
            raise HTTPException(
                status_code=403,
                detail=f"Bu işlem için {required_role} rolü gerekir."
            )
        
        return session
    
    return dependency


def get_current_user(request: Request) -> SessionUser | None:
    """Get current user from session (optional auth)."""
    session = get_session(request)
    return session.user if session else None


# Cookie-based API key authentication (for backward compatibility)
def require_api_key_cookie(request: Request) -> str:
    """Get API key from HttpOnly cookie (DASH-01 security fix).
    
    This replaces the insecure URL parameter/localStorage approach.
    """
    api_key = request.cookies.get("huginn_api_key", "")
    if not api_key:
        # Fallback to header for API clients
        api_key = request.headers.get("X-API-Key", "")
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API anahtarı gerekli. X-API-Key header veya huginn_api_key cookie."
        )
    
    return api_key