import uuid

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LoginCode(Base):
    __tablename__ = "login_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    attempts_left: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
