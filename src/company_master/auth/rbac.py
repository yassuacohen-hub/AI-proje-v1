"""RBAC (Role-Based Access Control) for Huginn Dashboard (DASH-01 S-3).

Roles hierarchy:
- Anon: No authentication required
- User: Basic authenticated user
- Analyst: Can access advanced features
- Admin: Full system access
"""

from __future__ import annotations

from typing import Literal

# Role definitions
ROLE_ANON: Literal["anon"] = "anon"
ROLE_USER: Literal["user"] = "user"
ROLE_ANALYST: Literal["analyst"] = "analyst"
ROLE_ADMIN: Literal["admin"] = "admin"

ROLES = {ROLE_ANON, ROLE_USER, ROLE_ANALYST, ROLE_ADMIN}

# Role hierarchy (higher index = more privileges)
ROLE_HIERARCHY = {
    ROLE_ANON: 0,
    ROLE_USER: 1,
    ROLE_ANALYST: 2,
    ROLE_ADMIN: 3,
}

# Role display names
ROLE_NAMES = {
    ROLE_ANON: "Anonim",
    ROLE_USER: "Kullanıcı",
    ROLE_ANALYST: "Analyst",
    ROLE_ADMIN: "Yönetici",
}

# Permissions mapping
ROLE_PERMISSIONS = {
    ROLE_ANON: ["read:public"],
    ROLE_USER: ["read:public", "read:companies", "read:own_profile"],
    ROLE_ANALYST: [
        "read:public",
        "read:companies",
        "read:own_profile",
        "read:quality_trend",
        "read:sources",
        "read:match",
        "export:csv",
    ],
    ROLE_ADMIN: [
        "read:public",
        "read:companies",
        "read:own_profile",
        "read:quality_trend",
        "read:sources",
        "read:match",
        "export:csv",
        "admin:users",
        "admin:approve",
        "admin:credit",
        "admin:categories",
        "admin:api_usage",
        "admin:audit_logs",
        "admin:rotate_keys",
    ],
}


def has_role(user_role: str, required_role: str) -> bool:
    """Check if user role meets or exceeds required role.

    Args:
        user_role: User's current role
        required_role: Minimum required role

    Returns:
        True if user has sufficient privileges
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    return user_level >= required_level


def has_permission(user_role: str, permission: str) -> bool:
    """Check if user role has specific permission.

    Args:
        user_role: User's current role
        permission: Permission string (e.g., "admin:users")

    Returns:
        True if user has the permission
    """
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    return permission in permissions


def require_admin(request: dict) -> bool:
    """Check if request has admin privileges.

    Args:
        request: Request dict with user info

    Returns:
        True if admin

    Raises:
        HTTPException: If not admin
    """
    user = request.get("user", {})
    if user.get("role") != ROLE_ADMIN:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="Yönetici yetkisi gerekiyor."
        )
    return True


def get_role_permissions(role: str) -> list[str]:
    """Get all permissions for a role."""
    return ROLE_PERMISSIONS.get(role, [])


def get_all_permissions() -> dict[str, list[str]]:
    """Get all role-permission mappings."""
    return dict(ROLE_PERMISSIONS)
