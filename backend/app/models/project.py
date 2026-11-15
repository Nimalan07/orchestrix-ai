import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, DateTime, func, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="created",
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

    # Relationships
    requirement = relationship(
        "Requirement",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )
    architecture = relationship(
        "Architecture",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Task.execution_order"
    )
    artifacts = relationship(
        "FileArtifact",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_projects_created_at", "created_at"),
    )
