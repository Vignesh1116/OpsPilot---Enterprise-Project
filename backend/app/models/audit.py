import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, TypeDecorator

from app.core.database import Base, GUID, UUIDMixin


class JSONType(TypeDecorator):
    """Platform-independent JSON type: JSONB on PostgreSQL, JSON on SQLite."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    company_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # CREATE, UPDATE, DELETE, STATUS_CHANGE, LOGIN
    entity_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # assets, users, locations, departments
    entity_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    old_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    new_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company")  # type: ignore # noqa: F821
    user: Mapped[Optional["User"]] = relationship("User")  # type: ignore # noqa: F821
