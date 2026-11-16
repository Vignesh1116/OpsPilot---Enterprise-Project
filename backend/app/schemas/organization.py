import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CompanyResponse(SchemaBase):
    id: uuid.UUID
    name: str
    slug: str
    code: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str
    email: EmailStr
    tax_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    tax_id: Optional[str] = None


class LocationResponse(SchemaBase):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    code: str
    type: str
    address: str
    city: str
    state: str
    postal_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LocationCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50, description="e.g. CBE-MF01")
    type: str = Field(
        ...,
        description="factory, warehouse, corporate_office, service_center, spare_parts_store",
    )
    address: str
    city: str
    state: str
    postal_code: str


class LocationUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(SchemaBase):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DepartmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50, description="e.g. MAINT, PROD")
    description: Optional[str] = None
