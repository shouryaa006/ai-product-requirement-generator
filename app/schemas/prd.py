"""Request and response shapes for PRD generation."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


NonEmptyString = Annotated[str, Field(min_length=1)]


class StrictBaseModel(BaseModel):
    """Base model for structured output with whitespace-normalized strings."""

    model_config = ConfigDict(str_strip_whitespace=True)


class PRDGenerateRequest(StrictBaseModel):
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


class Persona(StrictBaseModel):
    """One representative user of the product."""

    name: NonEmptyString
    role: NonEmptyString
    goals: list[NonEmptyString] = Field(min_length=1)
    pain_points: list[NonEmptyString] = Field(min_length=1)


class UserStory(StrictBaseModel):
    """A user story in the classic 'as a / I want / so that' form."""

    id: NonEmptyString = Field(pattern=r"^US-\d{3}$")
    as_a: NonEmptyString
    i_want: NonEmptyString
    so_that: NonEmptyString


class FunctionalRequirement(StrictBaseModel):
    """A stable, machine-readable functional requirement."""

    id: NonEmptyString = Field(pattern=r"^FR-\d{3}$")
    description: NonEmptyString
    priority: NonEmptyString


class NonFunctionalRequirement(StrictBaseModel):
    """A stable, machine-readable non-functional requirement."""

    id: NonEmptyString = Field(pattern=r"^NFR-\d{3}$")
    description: NonEmptyString
    category: NonEmptyString


class PRDDocument(StrictBaseModel):
    """Structured product requirements document returned by the API."""

    product_overview: NonEmptyString
    problem_statement: NonEmptyString
    target_users: list[NonEmptyString] = Field(min_length=1)
    personas: list[Persona] = Field(min_length=1)
    business_objectives: list[NonEmptyString] = Field(min_length=1)
    user_stories: list[UserStory] = Field(min_length=1)
    functional_requirements: list[FunctionalRequirement] = Field(min_length=1)
    non_functional_requirements: list[NonFunctionalRequirement] = Field(min_length=1)
    risks: list[NonEmptyString] = Field(min_length=1)
    assumptions: list[NonEmptyString] = Field(min_length=1)
    future_enhancements: list[NonEmptyString] = Field(min_length=1)

    @model_validator(mode="after")
    def ids_must_be_unique_and_sequential(self) -> "PRDDocument":
        """Require stable, predictable IDs within each structured output section."""
        _validate_sequential_ids(
            "user_stories",
            [story.id for story in self.user_stories],
            "US",
        )
        _validate_sequential_ids(
            "functional_requirements",
            [requirement.id for requirement in self.functional_requirements],
            "FR",
        )
        _validate_sequential_ids(
            "non_functional_requirements",
            [requirement.id for requirement in self.non_functional_requirements],
            "NFR",
        )
        return self


def _validate_sequential_ids(section: str, ids: list[str], prefix: str) -> None:
    if len(ids) != len(set(ids)):
        raise ValueError(f"{section} IDs must be unique")

    expected_ids = [f"{prefix}-{index:03d}" for index in range(1, len(ids) + 1)]
    if ids != expected_ids:
        raise ValueError(
            f"{section} IDs must be sequential: {', '.join(expected_ids)}"
        )
