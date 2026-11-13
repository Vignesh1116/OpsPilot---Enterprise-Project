import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth import Permission, Role, RolePermission, UserRole


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_code(
        self, code: str, company_id: Optional[uuid.UUID] = None
    ) -> Optional[Role]:
        """Fetch role by code, matching either company-specific or system default."""
        query = (
            select(Role)
            .options(
                selectinload(Role.role_permissions).selectinload(
                    RolePermission.permission
                )
            )
            .where(Role.code == code)
        )
        if company_id:
            query = query.where(
                (Role.company_id == company_id) | (Role.company_id.is_(None))
            )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_roles_by_codes(
        self, codes: List[str], company_id: Optional[uuid.UUID] = None
    ) -> List[Role]:
        """Fetch multiple roles by their codes."""
        query = (
            select(Role)
            .options(
                selectinload(Role.role_permissions).selectinload(
                    RolePermission.permission
                )
            )
            .where(Role.code.in_(codes))
        )
        if company_id:
            query = query.where(
                (Role.company_id == company_id) | (Role.company_id.is_(None))
            )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_or_create_permission(
        self, code: str, module: str, name: str, description: Optional[str] = None
    ) -> Permission:
        """Helper to bootstrap permissions."""
        result = await self.db.execute(
            select(Permission).where(Permission.code == code)
        )
        perm = result.scalars().first()
        if not perm:
            perm = Permission(
                code=code, module=module, name=name, description=description
            )
            self.db.add(perm)
            await self.db.flush()
        return perm

    async def get_or_create_system_role(
        self, code: str, name: str, description: Optional[str] = None
    ) -> Role:
        """Helper to bootstrap default system roles."""
        result = await self.db.execute(
            select(Role).where(Role.code == code, Role.company_id.is_(None))
        )
        role = result.scalars().first()
        if not role:
            role = Role(
                code=code,
                name=name,
                description=description,
                is_system_role=True,
                company_id=None,
            )
            self.db.add(role)
            await self.db.flush()
        return role

    async def attach_permission_to_role(self, role: Role, perm: Permission) -> None:
        """Attach a permission to a role if not already attached."""
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id,
            )
        )
        if not result.scalars().first():
            rp = RolePermission(role_id=role.id, permission_id=perm.id)
            self.db.add(rp)
            await self.db.flush()
