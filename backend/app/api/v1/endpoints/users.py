import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.auth import User
from app.schemas.auth import (
    UserCreateRequest,
    UserResponse,
    UserStatusUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List company users",
    dependencies=[Depends(require_roles("COMPANY_ADMIN", "OPERATIONS_MANAGER"))],
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[UserResponse]:
    """Retrieve paginated list of users within caller's company."""
    user_service = UserService(db)
    return await user_service.list_users(current_user, skip=skip, limit=limit)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user within company",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def create_user(
    user_in: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user. Strictly enforces that user is created in the creator's company."""
    user_service = UserService(db)
    return await user_service.create_user(current_user, user_in)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user details by ID",
    dependencies=[Depends(require_roles("COMPANY_ADMIN", "OPERATIONS_MANAGER"))],
)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Retrieve user details by ID, enforcing cross-company isolation."""
    user_service = UserService(db)
    return await user_service.get_user_by_id(current_user, user_id)


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Activate or deactivate a user account",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def update_user_status(
    user_id: uuid.UUID,
    status_in: UserStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Activate or deactivate user account within company."""
    user_service = UserService(db)
    return await user_service.update_user_status(
        current_user, user_id, status_in.is_active
    )
