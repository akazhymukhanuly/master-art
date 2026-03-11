from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(32), default="telegram", nullable=False)
    customer_name: Mapped[str] = mapped_column(String(128), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(64), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="ru")
    service_type: Mapped[str] = mapped_column(String(64), nullable=False)
    material: Mapped[str] = mapped_column(String(32), nullable=False, default="banner_frontlit")
    width_cm: Mapped[int] = mapped_column(Integer, nullable=False)
    height_cm: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    urgency_days: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    has_design: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delivery_type: Mapped[str] = mapped_column(String(16), nullable=False, default="pickup")
    delivery_address: Mapped[str] = mapped_column(Text, nullable=True, default="")
    notes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    estimated_price_kzt: Mapped[int] = mapped_column(Integer, nullable=False)
    estimate_detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
