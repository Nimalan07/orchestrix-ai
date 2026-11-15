from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10, max_length=10000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=10, max_length=10000)
    status: Literal[
        "created",
        "analyzing",
        "analyzed",
        "planning",
        "generating",
        "testing",
        "completed",
        "failed"
    ] | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
