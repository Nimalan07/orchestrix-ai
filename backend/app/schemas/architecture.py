from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class TechStack(BaseModel):
    frontend: str = Field(default="Next.js + TypeScript", description="Frontend framework")
    backend: str = Field(default="FastAPI", description="Backend web framework")
    database: str = Field(default="PostgreSQL", description="Primary persistence store")
    orm: str = Field(default="SQLAlchemy 2.x", description="Object Relational Mapper")
    authentication: str = Field(default="JWT (Bearer token)", description="Authentication strategy")
    styling: str = Field(default="Tailwind CSS", description="Styling library")
    testing: str = Field(default="Pytest + Playwright", description="Test frameworks")


class APIContract(BaseModel):
    endpoint: str = Field(description="REST path, e.g. /api/students")
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(description="HTTP method")
    description: str = Field(description="Purpose of endpoint")
    request_body: Optional[str] = Field(default=None, description="Expected request payload schema")
    response_body: str = Field(description="Expected response payload schema")
    auth_required: bool = Field(default=False, description="Whether authentication is required")


class EntityField(BaseModel):
    name: str = Field(description="Column name")
    type: str = Field(description="Data type (e.g. String(36), Integer, DateTime)")
    primary_key: bool = Field(default=False)
    nullable: bool = Field(default=False)
    unique: bool = Field(default=False)


class DataEntity(BaseModel):
    name: str = Field(description="Model/Class name, e.g. Student")
    table_name: str = Field(description="SQL table name, e.g. students")
    description: str = Field(description="Business description of entity")
    fields: List[EntityField] = Field(default_factory=list, description="Table columns")
    relationships: List[str] = Field(default_factory=list, description="Foreign keys and associations")


class ArchitecturalDecision(BaseModel):
    title: str = Field(description="Topic of architectural decision")
    decision: str = Field(description="Selected architecture choice")
    alternatives_considered: List[str] = Field(default_factory=list)
    trade_off: str = Field(description="Trade-offs or implications of this choice")


class SystemArchitecture(BaseModel):
    """Structured architectural blueprint produced by the Architect Agent."""

    project_name: str
    architecture_pattern: str = Field(
        default="Layered REST Architecture with SPA Client",
        description="High-level architecture pattern",
    )
    tech_stack: TechStack = Field(default_factory=TechStack)
    frontend_structure: List[str] = Field(
        default_factory=list, description="Key directories and pages in frontend"
    )
    backend_structure: List[str] = Field(
        default_factory=list, description="Key packages and modules in backend"
    )
    api_contracts: List[APIContract] = Field(
        default_factory=list, description="REST API contract definitions"
    )
    data_entities: List[DataEntity] = Field(
        default_factory=list, description="Database models and entity relationships"
    )
    security_guidelines: List[str] = Field(
        default_factory=list, description="Authentication, hashing, and authorization policies"
    )
    decisions: List[ArchitecturalDecision] = Field(
        default_factory=list, description="Key architectural trade-offs made"
    )

    model_config = ConfigDict(from_attributes=True)


class ArchitectureResponse(BaseModel):
    project_id: str
    status: str
    architecture: SystemArchitecture
