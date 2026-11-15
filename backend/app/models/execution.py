"""
ExecutionRun Database Model for tracking test runs and self-healing cycles.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base


class ExecutionRun(Base):
    """Tracks sandboxed test executions and self-healing cycles."""
    __tablename__ = "execution_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_type = Column(String(50), nullable=False, default="test")  # test, heal, build
    sandbox_mode = Column(String(50), nullable=False, default="local_process")  # docker, local_process
    status = Column(String(50), nullable=False, default="pending")  # pending, running, passed, failed, healed, error
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    iterations = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    diagnostic_report = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", backref="execution_runs")
