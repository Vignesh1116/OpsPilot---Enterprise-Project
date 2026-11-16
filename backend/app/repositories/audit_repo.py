import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditLog


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(
        self,
        company_id: uuid.UUID,
        action: str,
        entity_name: str,
        entity_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        log = AuditLog(
            company_id=company_id,
            user_id=user_id,
            action=action,
            entity_name=entity_name,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def list_by_entity(
        self,
        company_id: uuid.UUID,
        entity_name: str,
        entity_id: uuid.UUID,
        limit: int = 50,
    ) -> List[AuditLog]:
        query = (
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .where(
                AuditLog.company_id == company_id,
                AuditLog.entity_name == entity_name,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_by_company(
        self, company_id: uuid.UUID, limit: int = 100
    ) -> List[AuditLog]:
        query = (
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .where(AuditLog.company_id == company_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
