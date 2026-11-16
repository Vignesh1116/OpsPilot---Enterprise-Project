import base64
from datetime import date, datetime
import io
import json
import uuid
from typing import List, Optional, Tuple
import qrcode
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.asset import Asset, AssetCategory
from app.models.auth import User
from app.repositories.asset_repo import AssetCategoryRepository, AssetRepository
from app.repositories.audit_repo import AuditLogRepository
from app.repositories.organization_repo import DepartmentRepository, LocationRepository
from app.schemas.asset import (
    AssetCategoryCreateRequest,
    AssetCategoryResponse,
    AssetCreateRequest,
    AssetResponse,
    AssetUpdateRequest,
)
from app.schemas.audit import AuditLogResponse


def generate_qr_code_data_uri(content: str) -> str:
    """Generate a base64-encoded PNG Data URI for an asset QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


class AssetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.category_repo = AssetCategoryRepository(db)
        self.location_repo = LocationRepository(db)
        self.dept_repo = DepartmentRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def to_asset_response(self, asset: Asset) -> AssetResponse:
        """Map SQLAlchemy Asset model to AssetResponse with generated QR data URI."""
        qr_payload = json.dumps(
            {
                "id": str(asset.id),
                "asset_tag": asset.asset_tag,
                "name": asset.name,
                "company_id": str(asset.company_id),
                "serial_number": asset.serial_number,
                "model_number": asset.model_number,
                "status": asset.status,
            }
        )
        qr_uri = generate_qr_code_data_uri(qr_payload)

        return AssetResponse(
            id=asset.id,
            company_id=asset.company_id,
            location_id=asset.location_id,
            location_name=asset.location.name if asset.location else None,
            location_code=asset.location.code if asset.location else None,
            department_id=asset.department_id,
            department_name=asset.department.name if asset.department else None,
            category_id=asset.category_id,
            category_name=asset.category.name if asset.category else None,
            category_code=asset.category.code if asset.category else None,
            asset_tag=asset.asset_tag,
            name=asset.name,
            model_number=asset.model_number,
            serial_number=asset.serial_number,
            status=asset.status,
            critical_level=asset.critical_level,
            purchase_date=asset.purchase_date,
            purchase_cost=float(asset.purchase_cost),
            warranty_expiry_date=asset.warranty_expiry_date,
            expected_lifetime_months=asset.expected_lifetime_months,
            qr_code_url=asset.qr_code_url,
            qr_code_data_uri=qr_uri,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )

    # Asset Categories
    async def list_categories(self, caller: User) -> List[AssetCategoryResponse]:
        categories = await self.category_repo.list_by_company(caller.company_id)
        return [AssetCategoryResponse.model_validate(c) for c in categories]

    async def create_category(
        self, caller: User, cat_in: AssetCategoryCreateRequest
    ) -> AssetCategoryResponse:
        existing = await self.category_repo.get_by_code(
            cat_in.code, company_id=caller.company_id
        )
        if existing:
            raise ConflictError(
                f"An asset category with code '{cat_in.code}' already exists in your company."
            )

        cat = AssetCategory(
            company_id=caller.company_id,
            name=cat_in.name,
            code=cat_in.code.upper(),
            description=cat_in.description,
            depreciation_method=cat_in.depreciation_method,
            expected_lifetime_months=cat_in.expected_lifetime_months,
        )
        created = await self.category_repo.create(cat)

        await self.audit_repo.create_log(
            company_id=caller.company_id,
            user_id=caller.id,
            action="CREATE",
            entity_name="asset_categories",
            entity_id=created.id,
            new_values={"name": created.name, "code": created.code},
        )
        return AssetCategoryResponse.model_validate(created)

    # Assets
    async def create_asset(
        self, caller: User, asset_in: AssetCreateRequest
    ) -> AssetResponse:
        """Create a new industrial machinery or infrastructure asset with QR code."""
        # 1. Enforce unique asset_tag within company
        existing = await self.asset_repo.get_by_tag(
            asset_in.asset_tag, company_id=caller.company_id
        )
        if existing:
            raise ConflictError(
                f"An asset with code/tag '{asset_in.asset_tag}' already exists in your company."
            )

        # 2. Validate location belongs to caller's company
        loc = await self.location_repo.get_by_id(
            asset_in.location_id, company_id=caller.company_id
        )
        if not loc:
            raise ValidationError(
                "Assigned location does not exist or does not belong to your company."
            )

        # 3. Validate category belongs to caller's company
        cat = await self.category_repo.get_by_id(
            asset_in.category_id, company_id=caller.company_id
        )
        if not cat:
            raise ValidationError(
                "Assigned asset category does not exist or does not belong to your company."
            )

        # 4. Validate department belongs to caller's company (if provided)
        if asset_in.department_id:
            dept = await self.dept_repo.get_by_id(
                asset_in.department_id, company_id=caller.company_id
            )
            if not dept:
                raise ValidationError(
                    "Assigned department does not exist or does not belong to your company."
                )

        new_asset = Asset(
            company_id=caller.company_id,
            location_id=asset_in.location_id,
            department_id=asset_in.department_id,
            category_id=asset_in.category_id,
            asset_tag=asset_in.asset_tag.upper().strip(),
            name=asset_in.name.strip(),
            model_number=asset_in.model_number,
            serial_number=asset_in.serial_number,
            status=asset_in.status,
            critical_level=asset_in.critical_level,
            purchase_date=asset_in.purchase_date,
            purchase_cost=asset_in.purchase_cost,
            warranty_expiry_date=asset_in.warranty_expiry_date,
            expected_lifetime_months=asset_in.expected_lifetime_months,
            qr_code_url=f"/api/v1/assets/{asset_in.asset_tag.upper().strip()}/qr",
        )

        created_asset = await self.asset_repo.create(new_asset)

        # 5. Record audit trail
        await self.audit_repo.create_log(
            company_id=caller.company_id,
            user_id=caller.id,
            action="CREATE",
            entity_name="assets",
            entity_id=created_asset.id,
            new_values={
                "asset_tag": created_asset.asset_tag,
                "name": created_asset.name,
                "status": created_asset.status,
                "critical_level": created_asset.critical_level,
                "location_id": str(created_asset.location_id),
                "purchase_cost": float(created_asset.purchase_cost),
            },
        )

        return self.to_asset_response(created_asset)

    async def update_asset(
        self, caller: User, asset_id: uuid.UUID, update_in: AssetUpdateRequest
    ) -> AssetResponse:
        """Update specifications, location, warranty, or operational status of an asset."""
        asset = await self.asset_repo.get_by_id(
            asset_id, company_id=caller.company_id
        )
        if not asset:
            raise NotFoundError("Asset", asset_id)

        # Validate location if updating
        if update_in.location_id:
            loc = await self.location_repo.get_by_id(
                update_in.location_id, company_id=caller.company_id
            )
            if not loc:
                raise ValidationError("Assigned location does not belong to your company.")

        # Validate category if updating
        if update_in.category_id:
            cat = await self.category_repo.get_by_id(
                update_in.category_id, company_id=caller.company_id
            )
            if not cat:
                raise ValidationError("Assigned category does not belong to your company.")

        # Validate department if updating
        if update_in.department_id:
            dept = await self.dept_repo.get_by_id(
                update_in.department_id, company_id=caller.company_id
            )
            if not dept:
                raise ValidationError("Assigned department does not belong to your company.")

        update_dict = update_in.model_dump(exclude_unset=True)
        old_values = {}
        for k in update_dict.keys():
            if hasattr(asset, k):
                val = getattr(asset, k)
                old_values[k] = str(val) if isinstance(val, (uuid.UUID, date)) else val

        updated = await self.asset_repo.update(asset, update_dict)

        # Audit Log
        action = "STATUS_CHANGE" if "status" in update_dict and len(update_dict) == 1 else "UPDATE"
        await self.audit_repo.create_log(
            company_id=caller.company_id,
            user_id=caller.id,
            action=action,
            entity_name="assets",
            entity_id=updated.id,
            old_values=old_values,
            new_values={
                k: str(v) if isinstance(v, (uuid.UUID, date)) else v
                for k, v in update_dict.items()
            },
        )

        return self.to_asset_response(updated)

    async def get_asset(self, caller: User, asset_id: uuid.UUID) -> AssetResponse:
        """Fetch asset details strictly isolated to caller's company."""
        asset = await self.asset_repo.get_by_id(
            asset_id, company_id=caller.company_id
        )
        if not asset:
            raise NotFoundError("Asset", asset_id)
        return self.to_asset_response(asset)

    async def list_assets(
        self,
        caller: User,
        location_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        critical_level: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AssetResponse], int]:
        """Query assets with multi-field search and filters."""
        assets, total_count = await self.asset_repo.list_by_company(
            company_id=caller.company_id,
            location_id=location_id,
            category_id=category_id,
            status=status,
            critical_level=critical_level,
            search=search,
            skip=skip,
            limit=limit,
        )
        return [self.to_asset_response(a) for a in assets], total_count

    async def get_asset_history(
        self, caller: User, asset_id: uuid.UUID
    ) -> List[AuditLogResponse]:
        """Fetch historical audit log entries and status changes for an asset."""
        # Ensure asset exists in company first
        asset = await self.asset_repo.get_by_id(
            asset_id, company_id=caller.company_id
        )
        if not asset:
            raise NotFoundError("Asset", asset_id)

        logs = await self.audit_repo.list_by_entity(
            company_id=caller.company_id,
            entity_name="assets",
            entity_id=asset_id,
        )

        response_logs = []
        for log in logs:
            response_logs.append(
                AuditLogResponse(
                    id=log.id,
                    company_id=log.company_id,
                    user_id=log.user_id,
                    user_name=log.user.full_name if log.user else "System",
                    action=log.action,
                    entity_name=log.entity_name,
                    entity_id=log.entity_id,
                    old_values=log.old_values,
                    new_values=log.new_values,
                    ip_address=log.ip_address,
                    user_agent=log.user_agent,
                    created_at=log.created_at,
                )
            )
        return response_logs
