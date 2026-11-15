from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class FunctionalRequirement(BaseModel):
    id: str = Field(description="Unique requirement ID, e.g. FR-001")
    title: str = Field(description="Short title of the requirement")
    description: str = Field(description="Detailed functional description")
    priority: Literal["critical", "high", "medium", "low"] = Field(
        default="medium", description="Priority level of the requirement"
    )
    target_roles: List[str] = Field(
        default_factory=list, description="Roles that interact with this requirement"
    )


class NonFunctionalRequirement(BaseModel):
    category: Literal[
        "performance", "security", "scalability", "usability", "reliability", "maintainability"
    ] = Field(description="Category of non-functional requirement")
    description: str = Field(description="Specification of the quality attribute")
    metric: Optional[str] = Field(
        default=None, description="Measurable metric or target threshold"
    )


class UserRole(BaseModel):
    role: str = Field(description="Name of the user role, e.g. Admin, Student, Faculty")
    description: str = Field(description="Description of what this user does")
    permissions: List[str] = Field(
        default_factory=list, description="Permissions granted to this role"
    )


class FeatureModule(BaseModel):
    name: str = Field(description="Feature or module name")
    description: str = Field(description="Overview of the module purpose")
    components: List[str] = Field(
        default_factory=list, description="Key components or pages within this module"
    )


class TechnicalConstraint(BaseModel):
    category: str = Field(description="Category, e.g. Backend, Database, Auth, Frontend")
    constraint: str = Field(description="Technical constraint or rule")
    rationale: str = Field(description="Engineering rationale for this constraint")


class AcceptanceCriterion(BaseModel):
    id: str = Field(description="Identifier, e.g. AC-001")
    scenario: str = Field(description="User story or test scenario")
    given: str = Field(description="Initial condition / context")
    when: str = Field(description="Action executed by user or system")
    then: str = Field(description="Expected outcome or assertion")


class RequirementSpecification(BaseModel):
    """Structured, machine-readable requirement specification produced by Requirement Analyzer Agent."""

    project_name: str = Field(description="Name of the project")
    overview: str = Field(
        description="Comprehensive project summary and business purpose"
    )
    target_audience: str = Field(description="Primary users and consumers")
    user_roles: List[UserRole] = Field(
        description="Identified user roles and permissions"
    )
    functional_requirements: List[FunctionalRequirement] = Field(
        description="Comprehensive list of functional requirements"
    )
    non_functional_requirements: List[NonFunctionalRequirement] = Field(
        description="Performance, security, and scalability requirements"
    )
    core_features: List[FeatureModule] = Field(
        description="High-level feature modules and subsystems"
    )
    technical_constraints: List[TechnicalConstraint] = Field(
        description="Recommended technical constraints and architecture boundaries"
    )
    acceptance_criteria: List[AcceptanceCriterion] = Field(
        description="Testable Gherkin-style acceptance criteria"
    )
    clarifying_questions: List[str] = Field(
        default_factory=list,
        description="Questions identifying ambiguities or missing specifications in the user prompt",
    )
    complexity_score: Literal["low", "medium", "high", "enterprise"] = Field(
        default="medium", description="Estimated project complexity"
    )

    model_config = ConfigDict(from_attributes=True)


class RequirementAnalysisRequest(BaseModel):
    """Payload to trigger requirement analysis."""

    project_id: str
    additional_context: Optional[str] = Field(
        default=None,
        description="Optional additional instructions or preferences from the user",
    )


class RequirementAnalysisResponse(BaseModel):
    """API response after requirement analysis completes."""

    project_id: str
    status: str
    specification: RequirementSpecification
