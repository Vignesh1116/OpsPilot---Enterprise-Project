import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.auth import User
from app.models.organization import Company, CompanyLocation, Department
from app.repositories.audit_repo import AuditLogRepository
from app.repositories.organization_repo import (
    CompanyRepository,
    DepartmentRepository,
    LocationRepository,
)
from app.schemas.organization import (
    CompanyResponse,
    CompanyUpdateRequest,
    DepartmentCreateRequest,
    DepartmentResponse,
    LocationCreateRequest,
    LocationResponse,
    LocationUpdateRequest,
)


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.company_repo = CompanyRepository(db)
        self.location_repo = LocationRepository(db)
        self.dept_repo = DepartmentRepository(db)
        self.audit_repo = AuditLogRepository(db)

    async def get_company(self, caller: User) -> CompanyResponse:
        company = await self.company_repo.get_by_id(caller.company_id)
        if not company:
            raise NotFoundError("Company", caller.company_id)
        return CompanyResponse.model_validate(company)

    async def update_company(
        self, caller: User, update_in: CompanyUpdateRequest
    ) -> CompanyResponse:
        company = await self.company_repo.get_by_id(caller.company_id)
        if not company:
            raise NotFoundError("Company", caller.company_id)

        old_values = {
            "name": company.name,
            "address": company.address,
            "phone": company.phone,
            "email": company.email,
        }
        update_data = update_in.model_dump(exclude_unset=True)
        updated = await self.company_repo.update(company, update_data)

        await self.audit_repo.create_log(
            company_id=caller.company_id,
            user_id=caller.id,
            action="UPDATE",
            entity_name="companies",
            entity_id=company.id,
            old_values=old_values,
            new_values=update_data,
        )
        return CompanyResponse.model_validate(updated)

    async def list_locations(self, caller: User) -> List[LocationResponse]:
        locations = await self.location_repo.list_by_company(caller.company_id)
        return [LocationResponse.model_validate(loc) for loc in locations]

    async def get_location(
        self, caller: User, location_id: uuid.UUID
    ) -> LocationResponse:
        location = await self.location_repo.get_by_id(
            location_id, company_id=caller.company_id
        )
        if not location:
            raise NotFoundError("Location", location_id)
        return LocationResponse.model_validate(location)

    async def create_location(
        self, caller: User, location_in: LocationCreateRequest
    ) -> LocationResponse:
        existing = await self.location_repo.get_by_code(
            location_in.code, company_id=caller.company_id
        )
        if existing:
            raise ConflictError(
                f"A location with code '{location_in.code}' already exists in your company."
            )

        loc = CompanyLocation(
            company_id=caller.company_id,
            name=location_in.name,
            code=location_in.code.upper(),
            type=location_in.type,
            address=location_in.address,
            city=location_in.city,
            state=location_in.state,
            postal_code=location_in.postal_code,
            is_active=True,
        )
        created = await self.location_repo.create(loc)

        await self.audit_repo.create_log(
            company_id=caller.company_id,
            user_id=caller.id,
            action="CREATE",
            entity_name="company_locations",
            entity_id=created.id,
            new_values={"name": created.name, "code": created.code, "type": created.type},
        )
        return LocationResponse.model_validate(created)

    async def update_location(
        self, caller: User, location_id: uuid.UUID, update_in: LocationUpdateRequest
    ) -> LocationResponse:
        loc = await self.location_repo.get_by_id(
            location_id, company_id=caller.company_id
        )
        if not loc:
            raise NotFoundError("Location", location_id)

        update_data = update_in.model_dump(exclude_unset=True)
        old_values = {k: getattr(loc, k) for k in update_data.keys() if hasattr(loc, k)}
        updated = await self.location_repo.update(loc, update_data)

        await self.audit_repo.create_log(
            company_id=caller.company_id,
            user_id=caller.id,
            action="UPDATE",
            entity_name="company_locations",
            entity_id=loc.id,
            old_values=old_values,
            new_values=update_data,
        )
        return LocationResponse.model_validate(updated)

    async def list_departments(self, caller: User) -> List[DepartmentResponse]:
        departments = await self.dept_repo.list_by_company(caller.company_id)
        return [DepartmentResponse.model_validate(dept) for dept in departments]

    async def create_department(
        self, caller: User, dept_in: DepartmentCreateRequest
    ) -> DepartmentResponse:
        existing = await self.dept_repo.get_by_code(
            dept_in.code, company_id=caller.company_id
        )
        if existing:
            raise ConflictError(
                f"A department with code '{dept_in.code}' already exists in your company."
            )

        dept = Department(
            company_id=caller.company_id,
            name=dept_in.name,
            code=dept_in.code.upper(),
            description=dept_in.description,
            is_active=True,
        )
        created = await self.dept_repo.create(dept)

        await self.audit_repo.create_log(
            company_id=caller.company_id,
            user_id=caller.id,
            action="CREATE",
            entity_name="departments",
            entity_id=created.id,
            new_values={"name": created.name, "code": created.code},
        )
        return DepartmentResponse.model_validate(created)
