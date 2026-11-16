import uuid
from datetime import date
from typing import Optional
from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin, GUID


class AssetCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "asset_categories"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_company_asset_cat_code"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    depreciation_method: Mapped[str] = mapped_column(
        String(50), default="straight_line", nullable=False
    )
    expected_lifetime_months: Mapped[int] = mapped_column(default=120, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company")  # type: ignore # noqa: F821
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="category")


class Asset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_tag", name="uq_company_asset_tag"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("company_locations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("asset_categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    asset_tag: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    model_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(50), default="operational", nullable=False, index=True
    )  # operational, in_maintenance, out_of_service, decommissioned
    critical_level: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False, index=True
    )  # low, medium, high, critical
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    purchase_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    warranty_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_lifetime_months: Mapped[int] = mapped_column(default=120, nullable=False)
    qr_code_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company")  # type: ignore # noqa: F821
    location: Mapped["CompanyLocation"] = relationship("CompanyLocation")  # type: ignore # noqa: F821
    department: Mapped[Optional["Department"]] = relationship("Department")  # type: ignore # noqa: F821
    category: Mapped["AssetCategory"] = relationship("AssetCategory", back_populates="assets")
