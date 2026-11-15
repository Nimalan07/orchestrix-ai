import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    specification: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    project = relationship("Project", back_populates="requirement")

    __table_args__ = (
        Index("ix_requirements_project_id", "project_id"),
    )
