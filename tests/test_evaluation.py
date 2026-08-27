"""Tests for deterministic PRD evaluation metrics."""

from app.evaluation.metrics import evaluate_prd, evaluate_user_stories
from tests.sample_prd import SAMPLE_PRD


def test_complete_prd_gets_full_completeness_score():
    result = evaluate_prd(SAMPLE_PRD)

    assert result["completeness_score"] == 100.0
    assert result["passed_sections"] == 11
    assert result["total_sections"] == 11
    assert result["valid"] is True


def test_incomplete_prd_is_detected():
    incomplete_prd = dict(SAMPLE_PRD)
    incomplete_prd["risks"] = []

    result = evaluate_prd(incomplete_prd)

    assert result["completeness_score"] < 100.0
    assert result["passed_sections"] == 10
    assert result["total_sections"] == 11
    assert result["valid"] is False
    assert result["section_results"]["risks"] is False


def test_empty_string_section_is_detected():
    incomplete_prd = dict(SAMPLE_PRD)
    incomplete_prd["product_overview"] = "   "

    result = evaluate_prd(incomplete_prd)

    assert result["section_results"]["product_overview"] is False
    assert result["valid"] is False


def test_user_stories_get_full_score_when_complete():
    result = evaluate_user_stories(SAMPLE_PRD)

    assert result["score"] == 100.0
    assert result["total_stories"] == len(SAMPLE_PRD["user_stories"])
    assert result["valid_stories"] == result["total_stories"]
    assert result["valid"] is True


def test_incomplete_user_story_is_detected():
    incomplete_prd = dict(SAMPLE_PRD)
    incomplete_prd["user_stories"] = [
        {
            "as_a": "student",
            "i_want": "to find a tutor",
            "so_that": "",
        }
    ]

    result = evaluate_user_stories(incomplete_prd)

    assert result["score"] == 0.0
    assert result["total_stories"] == 1
    assert result["valid_stories"] == 0
    assert result["valid"] is False