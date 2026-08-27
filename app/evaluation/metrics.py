"""Deterministic evaluation metrics for generated PRDs."""

from typing import Any


REQUIRED_SECTIONS = [
    "product_overview",
    "problem_statement",
    "target_users",
    "personas",
    "business_objectives",
    "user_stories",
    "functional_requirements",
    "non_functional_requirements",
    "risks",
    "assumptions",
    "future_enhancements",
]


def evaluate_prd(prd: Any) -> dict[str, Any]:
    """Evaluate whether all required PRD sections are populated."""

    if hasattr(prd, "model_dump"):
        data = prd.model_dump()
    elif isinstance(prd, dict):
        data = prd
    else:
        raise TypeError("PRD must be a Pydantic model or dictionary.")

    section_results = {}
    passed_sections = 0

    for section in REQUIRED_SECTIONS:
        value = data.get(section)

        if isinstance(value, str):
            is_valid = bool(value.strip())
        elif isinstance(value, list):
            is_valid = len(value) > 0
        else:
            is_valid = value is not None

        section_results[section] = is_valid

        if is_valid:
            passed_sections += 1

    total_sections = len(REQUIRED_SECTIONS)
    completeness_score = round(
        (passed_sections / total_sections) * 100,
        2,
    )

    return {
        "completeness_score": completeness_score,
        "passed_sections": passed_sections,
        "total_sections": total_sections,
        "section_results": section_results,
        "valid": passed_sections == total_sections,
    }


def evaluate_user_stories(prd: Any) -> dict[str, Any]:
    """Evaluate the quality and completeness of PRD user stories."""

    if hasattr(prd, "model_dump"):
        data = prd.model_dump()
    elif isinstance(prd, dict):
        data = prd
    else:
        raise TypeError("PRD must be a Pydantic model or dictionary.")

    user_stories = data.get("user_stories", [])

    if not isinstance(user_stories, list) or not user_stories:
        return {
            "score": 0.0,
            "total_stories": 0,
            "valid_stories": 0,
            "valid": False,
        }

    valid_stories = 0

    for story in user_stories:
        if hasattr(story, "model_dump"):
            story = story.model_dump()

        if not isinstance(story, dict):
            continue

        as_a = str(story.get("as_a", "")).strip()
        i_want = str(story.get("i_want", "")).strip()
        so_that = str(story.get("so_that", "")).strip()

        if as_a and i_want and so_that:
            valid_stories += 1

    total_stories = len(user_stories)

    score = round(
        (valid_stories / total_stories) * 100,
        2,
    )

    return {
        "score": score,
        "total_stories": total_stories,
        "valid_stories": valid_stories,
        "valid": valid_stories == total_stories,
    }