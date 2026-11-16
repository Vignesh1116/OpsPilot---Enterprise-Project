import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.auth import User
from app.schemas.auth import (
    UserCreateRequest,
    UserResponse,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List and search company employees",
    dependencies=[Depends(require_roles("COMPANY_ADMIN", "OPERATIONS_MANAGER"))],
)
async def list_users(
    response: Response,
    search: Optional[str] = Query(None, description="Search by name, email, designation"),
    location_id: Optional[uuid.UUID] = Query(None, description="Filter by facility location"),
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by department"),
    is_active: Optional[bool] = Query(None, description="Filter active or deactivated"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[UserResponse]:
    """Retrieve filtered, paginated list of employees within caller's company."""
    user_service = UserService(db)
    items, total = await user_service.list_users(
        caller=current_user,
        location_id=location_id,
        department_id=department_id,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=limit,
    )
    response.headers["X-Total-Count"] = str(total)
    return items


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee within company",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def create_user(
    user_in: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new employee with location, department, and role assignment."""
    user_service = UserService(db)
    return await user_service.create_user(current_user, user_in)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get employee details by ID",
    dependencies=[Depends(require_roles("COMPANY_ADMIN", "OPERATIONS_MANAGER"))],
)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Retrieve employee details by ID, enforcing cross-company isolation."""
    user_service = UserService(db)
    return await user_service.get_user_by_id(current_user, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update employee details and assignments",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def update_user(
    user_id: uuid.UUID,
    update_in: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update employee details, designation, department, and location."""
    user_service = UserService(db)
    return await user_service.update_user(current_user, user_id, update_in)


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Activate or deactivate an employee account",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def update_user_status(
    user_id: uuid.UUID,
    status_in: UserStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Activate or deactivate employee account within company."""
    user_service = UserService(db)
    return await user_service.update_user_status(
        current_user, user_id, status_in.is_active
    )
