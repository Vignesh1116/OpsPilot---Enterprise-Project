import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AssetCategoryResponse(SchemaBase):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    depreciation_method: str
    expected_lifetime_months: int
    created_at: datetime
    updated_at: datetime


class AssetCategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50, description="e.g. SPIN-MACH, WEAV-LOOM")
    description: Optional[str] = None
    depreciation_method: str = Field("straight_line", description="straight_line, declining_balance")
    expected_lifetime_months: int = Field(120, ge=1, le=600)


class AssetResponse(SchemaBase):
    id: uuid.UUID
    company_id: uuid.UUID
    location_id: uuid.UUID
    location_name: Optional[str] = None
    location_code: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    department_name: Optional[str] = None
    category_id: uuid.UUID
    category_name: Optional[str] = None
    category_code: Optional[str] = None
    asset_tag: str
    name: str
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: str
    critical_level: str
    purchase_date: date
    purchase_cost: float
    warranty_expiry_date: Optional[date] = None
    expected_lifetime_months: int
    qr_code_url: Optional[str] = None
    qr_code_data_uri: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AssetCreateRequest(BaseModel):
    location_id: uuid.UUID
    department_id: Optional[uuid.UUID] = None
    category_id: uuid.UUID
    asset_tag: str = Field(..., min_length=2, max_length=100, description="Unique asset code e.g. AST-CBE-001")
    name: str = Field(..., min_length=2, max_length=255)
    model_number: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: str = Field(
        "operational",
        description="operational, in_maintenance, out_of_service, decommissioned",
    )
    critical_level: str = Field("medium", description="low, medium, high, critical")
    purchase_date: date
    purchase_cost: float = Field(..., ge=0.0)
    warranty_expiry_date: Optional[date] = None
    expected_lifetime_months: int = Field(120, ge=1, le=600)


class AssetUpdateRequest(BaseModel):
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[str] = Field(
        None, description="operational, in_maintenance, out_of_service, decommissioned"
    )
    critical_level: Optional[str] = Field(None, description="low, medium, high, critical")
    purchase_date: Optional[date] = None
    purchase_cost: Optional[float] = Field(None, ge=0.0)
    warranty_expiry_date: Optional[date] = None
    expected_lifetime_months: Optional[int] = Field(None, ge=1, le=600)
