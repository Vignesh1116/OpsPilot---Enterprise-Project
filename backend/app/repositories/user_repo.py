import uuid
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth import Role, RolePermission, User, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_query(self):
        """Standard query with eager loading of roles and permissions."""
        return select(User).options(
            selectinload(User.user_roles)
            .selectinload(UserRole.role)
            .selectinload(Role.role_permissions)
            .selectinload(RolePermission.permission)
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
        self, company_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> List[User]:
        """Fetch users strictly isolated to the caller's company."""
        query = (
            self._base_query()
            .where(User.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, user: User, roles: List[Role], assigned_by_id: Optional[uuid.UUID] = None) -> User:
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
        # Refresh with eager loaded relationships
        return await self.get_by_id(user.id, user.company_id)  # type: ignore

    async def update_status(self, user: User, is_active: bool) -> User:
        """Update active/disabled status."""
        user.is_active = is_active
        await self.db.flush()
        return user

    async def update_last_login(self, user: User) -> None:
        """Update last login timestamp."""
        from datetime import datetime, timezone
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()
