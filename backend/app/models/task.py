import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    task_key: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    assigned_agent: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False
    )
    dependencies: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False
    )
    execution_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    tier: Mapped[int] = mapped_column(
        Integer,
        default=0,
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

    project = relationship("Project", back_populates="tasks")

    __table_args__ = (
        Index("ix_tasks_project_order", "project_id", "execution_order"),
    )
