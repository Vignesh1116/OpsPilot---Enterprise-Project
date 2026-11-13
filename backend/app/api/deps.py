import uuid
from typing import Callable, List, Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.models.auth import User
from app.repositories.user_repo import UserRepository

# HTTPBearer security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency that extracts, verifies JWT, and resolves the active User entity."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedError("Authentication token is required.")

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception as e:
        raise UnauthorizedError(f"Could not validate credentials: {str(e)}")

    if payload.get("type") != "access":
        raise UnauthorizedError("Provided token is not an access token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Malformed credentials token.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid user identity in token.")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedError("User associated with this token does not exist.")

    if not user.is_active:
        raise UnauthorizedError("Account is inactive or disabled.")

    return user


def require_roles(*allowed_roles: str) -> Callable:
    """Dependency factory checking that current user belongs to one of allowed roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_codes = {r.code for r in current_user.roles}
        # COMPANY_ADMIN always has superuser authority across roles
        if "COMPANY_ADMIN" in user_role_codes:
            return current_user

        if not any(role in user_role_codes for role in allowed_roles):
            raise ForbiddenError(
                f"Role required: {', '.join(allowed_roles)}. Your roles: {', '.join(user_role_codes) or 'None'}"
            )
        return current_user

    return role_checker


def require_permissions(*required_permissions: str) -> Callable:
    """Dependency factory checking that current user holds required permissions."""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_codes = {r.code for r in current_user.roles}
        # COMPANY_ADMIN implicitly holds all permissions
        if "COMPANY_ADMIN" in user_role_codes:
            return current_user

        user_perms = set(current_user.permissions)
        missing_perms = [p for p in required_permissions if p not in user_perms]
        if missing_perms:
            raise ForbiddenError(
                f"Missing required permission(s): {', '.join(missing_perms)}"
            )
        return current_user

    return permission_checker
