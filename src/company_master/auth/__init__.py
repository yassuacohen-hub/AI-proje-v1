"""Auth & RBAC infrastructure for Huginn Dashboard (DASH-01 Phase 1).

Provides:
- HttpOnly cookie-based session management
- RBAC middleware with Anon/User/Analyst/Admin roles
- Supabase-compatible JWT verification
- Rate limiting per role
"""

from .session import (
    create_session,
    get_session,
    destroy_session,
    require_auth,
    require_role,
    get_current_user,
    SESSION_COOKIE_NAME,
    SESSION_TTL,
)
from .rbac import (
    ROLE_ANON,
    ROLE_USER,
    ROLE_ANALYST,
    ROLE_ADMIN,
    ROLES,
    ROLE_HIERARCHY,
    has_role,
    require_admin as rbac_require_admin,
)

__all__ = [
    "create_session",
    "get_session",
    "destroy_session",
    "require_auth",
    "require_role",
    "get_current_user",
    "SESSION_COOKIE_NAME",
    "SESSION_TTL",
    "ROLE_ANON",
    "ROLE_USER",
    "ROLE_ANALYST",
    "ROLE_ADMIN",
    "ROLES",
    "ROLE_HIERARCHY",
    "has_role",
]