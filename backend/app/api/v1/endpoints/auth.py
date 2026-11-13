from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.auth import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Authenticate user with email and password")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate and issue short-lived access and long-lived refresh JWTs."""
    auth_service = AuthService(db)
    token_response, _ = await auth_service.authenticate(
        email=credentials.email, password=credentials.password
    )
    return token_response


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Exchange a valid refresh token for a newly minted access token."""
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK, summary="End active session")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """Stateless logout endpoint (client removes tokens from storage)."""
    return {"message": "Successfully logged out.", "email": current_user.email}


@router.get("/me", response_model=UserResponse, summary="Get active user profile and permissions")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Returns the caller's complete profile, company context, assigned roles, and permissions."""
    user_service = UserService(db)
    return user_service.to_user_response(current_user)
