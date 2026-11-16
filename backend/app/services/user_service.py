import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.security import get_password_hash
from app.models.auth import User
from app.repositories.audit_repo import AuditLogRepository
from app.repositories.organization_repo import DepartmentRepository, LocationRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserCreateRequest, UserResponse, UserUpdateRequest


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.location_repo = LocationRepository(db)
        self.dept_repo = DepartmentRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def to_user_response(self, user: User) -> UserResponse:
        """Helper to map a User SQLAlchemy model to a clean UserResponse schema."""
        return UserResponse(
            id=user.id,
            company_id=user.company_id,
            location_id=user.location_id,
            location_name=user.location.name if user.location else None,
            department_id=user.department_id,
            department_name=user.department.name if user.department else None,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone=user.phone,
            designation=user.designation,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login_at=user.last_login_at,
            roles=[r.code for r in user.roles],
            permissions=user.permissions,
            created_at=user.created_at,
        )

    async def create_user(
        self, creator: User, user_in: UserCreateRequest
    ) -> UserResponse:
        """Create a new user/employee strictly isolated within the creator's company."""
        # 1. Check for existing email in company
        existing = await self.user_repo.get_by_email(
            user_in.email, company_id=creator.company_id
        )
        if existing:
            raise ConflictError(
                f"A user with email '{user_in.email}' already exists in your company."
            )

        # 2. Validate location assignment belongs to same company
        if user_in.location_id:
            loc = await self.location_repo.get_by_id(
                user_in.location_id, company_id=creator.company_id
            )
            if not loc:
                raise ValidationError(
                    f"Assigned location does not exist or does not belong to your company."
                )

        # 3. Validate department assignment belongs to same company
        if user_in.department_id:
            dept = await self.dept_repo.get_by_id(
                user_in.department_id, company_id=creator.company_id
            )
            if not dept:
                raise ValidationError(
                    f"Assigned department does not exist or does not belong to your company."
                )

        # 4. Resolve requested roles
        roles = await self.role_repo.get_roles_by_codes(
            user_in.role_codes, company_id=creator.company_id
        )
        if not roles:
            default_role = await self.role_repo.get_by_code("EMPLOYEE")
            if default_role:
                roles = [default_role]

        # 5. Securely hash password
        hashed_password = get_password_hash(user_in.password)

        # 6. Construct user entity with creator's company_id
        new_user = User(
            company_id=creator.company_id,
            location_id=user_in.location_id or creator.location_id,
            department_id=user_in.department_id,
            email=user_in.email.lower().strip(),
            password_hash=hashed_password,
            first_name=user_in.first_name.strip(),
            last_name=user_in.last_name.strip(),
            phone=user_in.phone,
            designation=user_in.designation,
            is_active=True,
            is_verified=True,
        )

        created_user = await self.user_repo.create(
            new_user, roles=roles, assigned_by_id=creator.id
        )

        # 7. Audit Log
        await self.audit_repo.create_log(
            company_id=creator.company_id,
            user_id=creator.id,
            action="CREATE",
            entity_name="users",
            entity_id=created_user.id,
            new_values={
                "email": created_user.email,
                "first_name": created_user.first_name,
                "last_name": created_user.last_name,
                "location_id": str(created_user.location_id) if created_user.location_id else None,
                "department_id": str(created_user.department_id) if created_user.department_id else None,
                "roles": [r.code for r in created_user.roles],
            },
        )

        return self.to_user_response(created_user)

    async def update_user(
        self, creator: User, target_user_id: uuid.UUID, update_in: UserUpdateRequest
    ) -> UserResponse:
        """Update employee details, department, location, or roles."""
        target_user = await self.user_repo.get_by_id(
            target_user_id, company_id=creator.company_id
        )
        if not target_user:
            raise NotFoundError("User", target_user_id)

        # Validate location if updating
        if update_in.location_id:
            loc = await self.location_repo.get_by_id(
                update_in.location_id, company_id=creator.company_id
            )
            if not loc:
                raise ValidationError("Assigned location does not belong to your company.")

        # Validate department if updating
        if update_in.department_id:
            dept = await self.dept_repo.get_by_id(
                update_in.department_id, company_id=creator.company_id
            )
            if not dept:
                raise ValidationError("Assigned department does not belong to your company.")

        update_dict = update_in.model_dump(exclude_unset=True, exclude={"role_codes"})
        old_values = {
            "first_name": target_user.first_name,
            "last_name": target_user.last_name,
            "phone": target_user.phone,
            "designation": target_user.designation,
            "location_id": str(target_user.location_id) if target_user.location_id else None,
            "department_id": str(target_user.department_id) if target_user.department_id else None,
        }

        updated_user = await self.user_repo.update(target_user, update_dict)

        # Update roles if specified
        if update_in.role_codes is not None:
            new_roles = await self.role_repo.get_roles_by_codes(
                update_in.role_codes, company_id=creator.company_id
            )
            await self.user_repo.update_roles(
                updated_user, new_roles, assigned_by_id=creator.id
            )
            updated_user = await self.user_repo.get_by_id(
                updated_user.id, creator.company_id
            )

        # Audit Log
        await self.audit_repo.create_log(
            company_id=creator.company_id,
            user_id=creator.id,
            action="UPDATE",
            entity_name="users",
            entity_id=updated_user.id,  # type: ignore
            old_values=old_values,
            new_values=update_dict,
        )

        return self.to_user_response(updated_user)  # type: ignore

    async def update_user_status(
        self, creator: User, target_user_id: uuid.UUID, is_active: bool
    ) -> UserResponse:
        """Activate or deactivate a user account with isolation check and audit trail."""
        if creator.id == target_user_id and not is_active:
            raise ForbiddenError("Administrators cannot deactivate their own account.")

        target_user = await self.user_repo.get_by_id(
            target_user_id, company_id=creator.company_id
        )
        if not target_user:
            raise NotFoundError("User", target_user_id)

        old_status = target_user.is_active
        updated_user = await self.user_repo.update_status(target_user, is_active)

        await self.audit_repo.create_log(
            company_id=creator.company_id,
            user_id=creator.id,
            action="STATUS_CHANGE",
            entity_name="users",
            entity_id=updated_user.id,
            old_values={"is_active": old_status},
            new_values={"is_active": is_active},
        )
        return self.to_user_response(updated_user)

    async def get_user_by_id(
        self, caller: User, target_user_id: uuid.UUID
    ) -> UserResponse:
        """Get user details strictly scoped to caller's company."""
        user = await self.user_repo.get_by_id(
            target_user_id, company_id=caller.company_id
        )
        if not user:
            raise NotFoundError("User", target_user_id)
        return self.to_user_response(user)

    async def list_users(
        self,
        caller: User,
        location_id: Optional[uuid.UUID] = None,
        department_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[UserResponse], int]:
        """List and search users for caller's company."""
        users, total = await self.user_repo.list_by_company(
            company_id=caller.company_id,
            location_id=location_id,
            department_id=department_id,
            is_active=is_active,
            search=search,
            skip=skip,
            limit=limit,
        )
        return [self.to_user_response(u) for u in users], total
