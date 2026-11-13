import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import get_password_hash
from app.models.auth import User
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserCreateRequest, UserResponse


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def to_user_response(self, user: User) -> UserResponse:
        """Helper to map a User SQLAlchemy model to a clean UserResponse schema."""
        return UserResponse(
            id=user.id,
            company_id=user.company_id,
            location_id=user.location_id,
            department_id=user.department_id,
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
        """Create a new user strictly isolated within the creator's company."""
        # 1. Check for existing email in company
        existing = await self.user_repo.get_by_email(
            user_in.email, company_id=creator.company_id
        )
        if existing:
            raise ConflictError(
                f"A user with email '{user_in.email}' already exists in your company."
            )

        # 2. Resolve requested roles
        roles = await self.role_repo.get_roles_by_codes(
            user_in.role_codes, company_id=creator.company_id
        )
        if not roles:
            # Fallback to EMPLOYEE if none matched
            default_role = await self.role_repo.get_by_code("EMPLOYEE")
            if default_role:
                roles = [default_role]

        # 3. Securely hash password
        hashed_password = get_password_hash(user_in.password)

        # 4. Construct user entity with creator's company_id
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
        return self.to_user_response(created_user)

    async def update_user_status(
        self, creator: User, target_user_id: uuid.UUID, is_active: bool
    ) -> UserResponse:
        """Activate or deactivate a user account with isolation check."""
        if creator.id == target_user_id and not is_active:
            raise ForbiddenError("Administrators cannot deactivate their own account.")

        target_user = await self.user_repo.get_by_id(
            target_user_id, company_id=creator.company_id
        )
        if not target_user:
            raise NotFoundError("User", target_user_id)

        updated_user = await self.user_repo.update_status(target_user, is_active)
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
        self, caller: User, skip: int = 0, limit: int = 50
    ) -> List[UserResponse]:
        """List users for caller's company."""
        users = await self.user_repo.list_by_company(
            caller.company_id, skip=skip, limit=limit
        )
        return [self.to_user_response(u) for u in users]
