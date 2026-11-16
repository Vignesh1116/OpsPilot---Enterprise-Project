import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.auth import User
from app.schemas.organization import (
    CompanyResponse,
    CompanyUpdateRequest,
    DepartmentCreateRequest,
    DepartmentResponse,
    LocationCreateRequest,
    LocationResponse,
    LocationUpdateRequest,
)
from app.services.organization_service import OrganizationService

router = APIRouter()


# Company Endpoints
@router.get("/company", response_model=CompanyResponse, summary="Get company profile")
async def get_company(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    org_service = OrganizationService(db)
    return await org_service.get_company(current_user)


@router.put(
    "/company",
    response_model=CompanyResponse,
    summary="Update company profile",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def update_company(
    update_in: CompanyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    org_service = OrganizationService(db)
    return await org_service.update_company(current_user, update_in)


# Locations Endpoints
@router.get("/locations", response_model=List[LocationResponse], summary="List operating facilities")
async def list_locations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[LocationResponse]:
    org_service = OrganizationService(db)
    return await org_service.list_locations(current_user)


@router.post(
    "/locations",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new operating facility",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def create_location(
    location_in: LocationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    org_service = OrganizationService(db)
    return await org_service.create_location(current_user, location_in)


@router.get("/locations/{location_id}", response_model=LocationResponse, summary="Get facility details")
async def get_location(
    location_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    org_service = OrganizationService(db)
    return await org_service.get_location(current_user, location_id)


@router.put(
    "/locations/{location_id}",
    response_model=LocationResponse,
    summary="Update facility details",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def update_location(
    location_id: uuid.UUID,
    update_in: LocationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    org_service = OrganizationService(db)
    return await org_service.update_location(current_user, location_id, update_in)


# Departments Endpoints
@router.get("/departments", response_model=List[DepartmentResponse], summary="List company departments")
async def list_departments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DepartmentResponse]:
    org_service = OrganizationService(db)
    return await org_service.list_departments(current_user)


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new department",
    dependencies=[Depends(require_roles("COMPANY_ADMIN"))],
)
async def create_department(
    dept_in: DepartmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DepartmentResponse:
    org_service = OrganizationService(db)
    return await org_service.create_department(current_user, dept_in)
