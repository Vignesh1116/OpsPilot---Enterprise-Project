import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Company, CompanyLocation, Department


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        result = await self.db.execute(
            select(Company).where(Company.id == company_id)
        )
        return result.scalars().first()

    async def update(self, company: Company, update_data: dict) -> Company:
        for key, value in update_data.items():
            if value is not None:
                setattr(company, key, value)
        await self.db.flush()
        return company


class LocationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, location_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> Optional[CompanyLocation]:
        query = select(CompanyLocation).where(CompanyLocation.id == location_id)
        if company_id:
            query = query.where(CompanyLocation.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_code(
        self, code: str, company_id: uuid.UUID
    ) -> Optional[CompanyLocation]:
        result = await self.db.execute(
            select(CompanyLocation).where(
                CompanyLocation.code == code, CompanyLocation.company_id == company_id
            )
        )
        return result.scalars().first()

    async def list_by_company(self, company_id: uuid.UUID) -> List[CompanyLocation]:
        result = await self.db.execute(
            select(CompanyLocation)
            .where(CompanyLocation.company_id == company_id)
            .order_by(CompanyLocation.name.asc())
        )
        return list(result.scalars().all())

    async def create(self, location: CompanyLocation) -> CompanyLocation:
        self.db.add(location)
        await self.db.flush()
        return location

    async def update(
        self, location: CompanyLocation, update_data: dict
    ) -> CompanyLocation:
        for key, value in update_data.items():
            if value is not None:
                setattr(location, key, value)
        await self.db.flush()
        return location


class DepartmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, department_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> Optional[Department]:
        query = select(Department).where(Department.id == department_id)
        if company_id:
            query = query.where(Department.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_code(
        self, code: str, company_id: uuid.UUID
    ) -> Optional[Department]:
        result = await self.db.execute(
            select(Department).where(
                Department.code == code, Department.company_id == company_id
            )
        )
        return result.scalars().first()

    async def list_by_company(self, company_id: uuid.UUID) -> List[Department]:
        result = await self.db.execute(
            select(Department)
            .where(Department.company_id == company_id)
            .order_by(Department.name.asc())
        )
        return list(result.scalars().all())

    async def create(self, department: Department) -> Department:
        self.db.add(department)
        await self.db.flush()
        return department
