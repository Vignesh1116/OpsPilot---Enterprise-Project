import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth import Role, RolePermission, User, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_query(self):
        """Standard query with eager loading of location, department, roles, and permissions."""
        return select(User).options(
            selectinload(User.location),
            selectinload(User.department),
            selectinload(User.user_roles)
            .selectinload(UserRole.role)
            .selectinload(Role.role_permissions)
            .selectinload(RolePermission.permission),
        )

    async def get_by_id(
        self, user_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> Optional[User]:
        """Fetch user by primary key, strictly isolating by company_id when passed."""
        query = self._base_query().where(User.id == user_id)
        if company_id is not None:
            query = query.where(User.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_email(
        self, email: str, company_id: Optional[uuid.UUID] = None
    ) -> Optional[User]:
        """Fetch user by email and optional company_id."""
        query = self._base_query().where(User.email == email.lower())
        if company_id is not None:
            query = query.where(User.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_by_company(
        self,
        company_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None,
        department_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[User], int]:
        """Fetch users strictly isolated to the caller's company with multi-field search and filters."""
        query = self._base_query().where(User.company_id == company_id)
        count_query = select(func.count(User.id)).where(User.company_id == company_id)

        if location_id:
            query = query.where(User.location_id == location_id)
            count_query = count_query.where(User.location_id == location_id)

        if department_id:
            query = query.where(User.department_id == department_id)
            count_query = count_query.where(User.department_id == department_id)

        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)

        if search:
            search_filter = or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.designation.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_res = await self.db.execute(count_query)
        total_count = total_res.scalar() or 0

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        items_res = await self.db.execute(query)
        items = list(items_res.scalars().all())

        return items, total_count

    async def create(
        self, user: User, roles: List[Role], assigned_by_id: Optional[uuid.UUID] = None
    ) -> User:
        """Persist a new user and assign roles within the same transaction."""
        self.db.add(user)
        await self.db.flush()

        for role in roles:
            user_role = UserRole(
                user_id=user.id,
                role_id=role.id,
                assigned_by=assigned_by_id,
            )
            self.db.add(user_role)

        await self.db.flush()
        return await self.get_by_id(user.id, user.company_id)  # type: ignore

    async def update(self, user: User, update_data: dict) -> User:
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        await self.db.flush()
        return await self.get_by_id(user.id, user.company_id)  # type: ignore

    async def update_roles(
        self, user: User, new_roles: List[Role], assigned_by_id: Optional[uuid.UUID] = None
    ) -> None:
        """Replace user roles with new role assignments."""
        for ur in list(user.user_roles):
            await self.db.delete(ur)
        await self.db.flush()

        for role in new_roles:
            ur = UserRole(
                user_id=user.id,
                role_id=role.id,
                assigned_by=assigned_by_id,
            )
            self.db.add(ur)
        await self.db.flush()

    async def update_status(self, user: User, is_active: bool) -> User:
        """Update active/disabled status."""
        user.is_active = is_active
        await self.db.flush()
        return await self.get_by_id(user.id, user.company_id)  # type: ignore

    async def update_last_login(self, user: User) -> None:
        """Update last login timestamp."""
        from datetime import datetime, timezone
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()
