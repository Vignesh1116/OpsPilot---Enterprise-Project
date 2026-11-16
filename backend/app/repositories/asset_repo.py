import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asset import Asset, AssetCategory


class AssetCategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, category_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> Optional[AssetCategory]:
        query = select(AssetCategory).where(AssetCategory.id == category_id)
        if company_id:
            query = query.where(AssetCategory.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_code(
        self, code: str, company_id: uuid.UUID
    ) -> Optional[AssetCategory]:
        result = await self.db.execute(
            select(AssetCategory).where(
                AssetCategory.code == code, AssetCategory.company_id == company_id
            )
        )
        return result.scalars().first()

    async def list_by_company(self, company_id: uuid.UUID) -> List[AssetCategory]:
        result = await self.db.execute(
            select(AssetCategory)
            .where(AssetCategory.company_id == company_id)
            .order_by(AssetCategory.name.asc())
        )
        return list(result.scalars().all())

    async def create(self, category: AssetCategory) -> AssetCategory:
        self.db.add(category)
        await self.db.flush()
        return category


class AssetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_query(self):
        return select(Asset).options(
            selectinload(Asset.location),
            selectinload(Asset.department),
            selectinload(Asset.category),
        )

    async def get_by_id(
        self, asset_id: uuid.UUID, company_id: Optional[uuid.UUID] = None
    ) -> Optional[Asset]:
        query = self._base_query().where(Asset.id == asset_id)
        if company_id:
            query = query.where(Asset.company_id == company_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_tag(
        self, asset_tag: str, company_id: uuid.UUID
    ) -> Optional[Asset]:
        query = self._base_query().where(
            Asset.asset_tag == asset_tag, Asset.company_id == company_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_by_company(
        self,
        company_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        critical_level: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Asset], int]:
        """Fetch assets strictly isolated by company_id with multi-field search and filters."""
        query = self._base_query().where(Asset.company_id == company_id)
        count_query = select(func.count(Asset.id)).where(Asset.company_id == company_id)

        if location_id:
            query = query.where(Asset.location_id == location_id)
            count_query = count_query.where(Asset.location_id == location_id)

        if category_id:
            query = query.where(Asset.category_id == category_id)
            count_query = count_query.where(Asset.category_id == category_id)

        if status:
            query = query.where(Asset.status == status)
            count_query = count_query.where(Asset.status == status)

        if critical_level:
            query = query.where(Asset.critical_level == critical_level)
            count_query = count_query.where(Asset.critical_level == critical_level)

        if search:
            search_filter = or_(
                Asset.name.ilike(f"%{search}%"),
                Asset.asset_tag.ilike(f"%{search}%"),
                Asset.serial_number.ilike(f"%{search}%"),
                Asset.model_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar() or 0

        query = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit)
        items_result = await self.db.execute(query)
        items = list(items_result.scalars().all())

        return items, total_count

    async def create(self, asset: Asset) -> Asset:
        self.db.add(asset)
        await self.db.flush()
        return await self.get_by_id(asset.id, asset.company_id)  # type: ignore

    async def update(self, asset: Asset, update_data: dict) -> Asset:
        for key, value in update_data.items():
            if value is not None:
                setattr(asset, key, value)
        await self.db.flush()
        return await self.get_by_id(asset.id, asset.company_id)  # type: ignore
