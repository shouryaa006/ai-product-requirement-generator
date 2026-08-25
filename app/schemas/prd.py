"""Request and response shapes for PRD generation."""

from pydantic import BaseModel, Field, field_validator


class PRDGenerateRequest(BaseModel):
    """Incoming body for POST /api/v1/prd/generate."""

    product_idea: str = Field(
        ...,
        description="A short description of the product you want a PRD for.",
        examples=["I want to build an app where college students can find tutors."],
    )

    @field_validator("product_idea")
    @classmethod
    def product_idea_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("product_idea must not be empty")
        return cleaned


class Persona(BaseModel):
    """One representative user of the product."""

    name: str
    role: str
    goals: list[str]
    pain_points: list[str]


class UserStory(BaseModel):
    """A user story in the classic 'as a / I want / so that' form."""

    as_a: str
    i_want: str
    so_that: str


class PRDDocument(BaseModel):
    """Structured product requirements document returned by the API."""

    product_overview: str
    problem_statement: str
    target_users: list[str]
    personas: list[Persona]
    business_objectives: list[str]
    user_stories: list[UserStory]
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    risks: list[str]
    assumptions: list[str]
    future_enhancements: list[str]
