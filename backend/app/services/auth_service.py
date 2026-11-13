import uuid
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.auth import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, UserResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def authenticate(self, email: str, password: str) -> Tuple[TokenResponse, User]:
        """Authenticate user by email and password, returning tokens if valid and active."""
        user = await self.user_repo.get_by_email(email)

        if not user:
            # Constant-time mitigation against timing attacks
            verify_password("dummy-password", "$2b$12$e80yq9gW5zK7j.vYv2c/..8Q6w46uVqZkJcR5n8u9/p6eU6.LgG9e")
            raise UnauthorizedError("Invalid email or password.")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")

        # Account status validation
        if not user.is_active:
            raise UnauthorizedError("User account has been disabled. Contact your company administrator.")

        # Update last login
        await self.user_repo.update_last_login(user)

        # Build token claims
        role_codes = [r.code for r in user.roles]
        permissions = user.permissions

        claims = {
            "company_id": str(user.company_id),
            "email": user.email,
            "roles": role_codes,
            "permissions": permissions,
        }

        access_token = create_access_token(subject=user.id, claims=claims)
        refresh_token = create_refresh_token(subject=user.id)

        user_response = UserResponse(
            id=user.id,
            company_id=user.company_id,
            location_id=user.location_id,
            department_id=user.department_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone=user.phone,
            designation=user.designation,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login_at=user.last_login_at,
            roles=role_codes,
            permissions=permissions,
            created_at=user.created_at,
        )

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response,
        )

        return token_response, user

    async def refresh_tokens(self, refresh_token_str: str) -> TokenResponse:
        """Validate refresh token and issue new token pair."""
        try:
            payload = decode_token(refresh_token_str)
        except Exception as e:
            raise UnauthorizedError("Invalid or expired refresh token.") from e

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Provided token is not a valid refresh token.")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedError("Malformed token payload.")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise UnauthorizedError("Invalid user identifier in token.")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User is no longer active.")

        role_codes = [r.code for r in user.roles]
        permissions = user.permissions

        claims = {
            "company_id": str(user.company_id),
            "email": user.email,
            "roles": role_codes,
            "permissions": permissions,
        }

        new_access_token = create_access_token(subject=user.id, claims=claims)
        new_refresh_token = create_refresh_token(subject=user.id)

        user_response = UserResponse(
            id=user.id,
            company_id=user.company_id,
            location_id=user.location_id,
            department_id=user.department_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone=user.phone,
            designation=user.designation,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login_at=user.last_login_at,
            roles=role_codes,
            permissions=permissions,
            created_at=user.created_at,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response,
        )
