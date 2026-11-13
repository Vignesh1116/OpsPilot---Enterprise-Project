import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Base Schema with modern Pydantic v2 ConfigDict
class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PermissionResponse(SchemaBase):
    id: uuid.UUID
    code: str
    module: str
    name: str
    description: Optional[str] = None


class RoleResponse(SchemaBase):
    id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    permissions: List[str] = []


class UserResponse(SchemaBase):
    id: uuid.UUID
    company_id: uuid.UUID
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    roles: List[str] = []
    permissions: List[str] = []
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Plaintext user password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserResponse


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters password")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=25)
    designation: Optional[str] = Field(None, max_length=100)
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    role_codes: List[str] = Field(
        default=["EMPLOYEE"],
        description="Assigned role codes (e.g. OPERATIONS_MANAGER, MAINTENANCE_TECHNICIAN, INVENTORY_EXECUTIVE, EMPLOYEE)",
    )


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None


class UserStatusUpdateRequest(BaseModel):
    is_active: bool = Field(..., description="True to activate account, False to disable")
