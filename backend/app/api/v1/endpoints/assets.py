import io
import json
import uuid
from typing import List, Optional
import qrcode
from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.auth import User
from app.schemas.asset import (
    AssetCategoryCreateRequest,
    AssetCategoryResponse,
    AssetCreateRequest,
    AssetResponse,
    AssetUpdateRequest,
)
from app.schemas.audit import AuditLogResponse
from app.services.asset_service import AssetService

router = APIRouter()


# Categories
@router.get(
    "/categories",
    response_model=List[AssetCategoryResponse],
    summary="List asset categories",
)
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[AssetCategoryResponse]:
    asset_service = AssetService(db)
    return await asset_service.list_categories(current_user)


@router.post(
    "/categories",
    response_model=AssetCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new asset category",
    dependencies=[Depends(require_roles("COMPANY_ADMIN", "OPERATIONS_MANAGER"))],
)
async def create_category(
    cat_in: AssetCategoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AssetCategoryResponse:
    asset_service = AssetService(db)
    return await asset_service.create_category(current_user, cat_in)


# Assets
@router.get("", response_model=List[AssetResponse], summary="List and search assets")
async def list_assets(
    response: Response,
    search: Optional[str] = Query(None, description="Search by name, tag, model, serial"),
    location_id: Optional[uuid.UUID] = Query(None, description="Filter by location"),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="operational, in_maintenance, out_of_service, decommissioned"),
    critical_level: Optional[str] = Query(None, description="low, medium, high, critical"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[AssetResponse]:
    """Retrieve filtered, paginated list of assets for the caller's company."""
    asset_service = AssetService(db)
    items, total = await asset_service.list_assets(
        caller=current_user,
        location_id=location_id,
        category_id=category_id,
        status=status,
        critical_level=critical_level,
        search=search,
        skip=skip,
        limit=limit,
    )
    response.headers["X-Total-Count"] = str(total)
    return items


@router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new asset",
    dependencies=[Depends(require_roles("COMPANY_ADMIN", "OPERATIONS_MANAGER"))],
)
async def create_asset(
    asset_in: AssetCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AssetResponse:
    """Register an industrial machinery, electronic, or infrastructure asset."""
    asset_service = AssetService(db)
    return await asset_service.create_asset(current_user, asset_in)


@router.get("/{asset_id}", response_model=AssetResponse, summary="Get asset details with QR code")
async def get_asset(
    asset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AssetResponse:
    """Get complete asset record including location, department, category, and QR data URI."""
    asset_service = AssetService(db)
    return await asset_service.get_asset(current_user, asset_id)


@router.put(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Update asset specifications and status",
    dependencies=[Depends(require_roles("COMPANY_ADMIN", "OPERATIONS_MANAGER"))],
)
async def update_asset(
    asset_id: uuid.UUID,
    update_in: AssetUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AssetResponse:
    """Update asset specifications, status, location, or warranty."""
    asset_service = AssetService(db)
    return await asset_service.update_asset(current_user, asset_id, update_in)


@router.get(
    "/{asset_id}/history",
    response_model=List[AuditLogResponse],
    summary="Get asset audit and status transition history",
)
async def get_asset_history(
    asset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[AuditLogResponse]:
    """Retrieve chronological audit timeline of all modifications on this asset."""
    asset_service = AssetService(db)
    return await asset_service.get_asset_history(current_user, asset_id)


@router.get("/{asset_id}/qr", summary="Download/Stream raw PNG QR code")
async def download_asset_qr(
    asset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and stream a high-resolution PNG QR code for equipment labeling."""
    asset_service = AssetService(db)
    asset = await asset_service.get_asset(current_user, asset_id)

    qr_payload = json.dumps(
        {
            "id": str(asset.id),
            "asset_tag": asset.asset_tag,
            "name": asset.name,
            "company_id": str(asset.company_id),
            "status": asset.status,
        }
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    filename = f"qr_{asset.asset_tag.lower()}.png"
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
