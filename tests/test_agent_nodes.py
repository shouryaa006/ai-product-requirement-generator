"""Deterministic tests for individual multi-agent workflow nodes."""

import json
from unittest.mock import MagicMock

from app.agents.business_analyst import BusinessAnalystAgent
from app.agents.planner import PlannerAgent
from app.agents.prd_generator import PRDGeneratorAgent
from app.agents.product_manager import ProductManagerAgent
from app.schemas.prd import PRDDocument
from tests.sample_prd import SAMPLE_PRD


def make_agent_state(**overrides):
    state = {
        "product_idea": "An app where college students can find tutors.",
        "retrieved_context": "",
        "planner_output": "Planner analysis",
        "business_analyst_output": "Business analysis",
        "product_manager_output": "Product requirements",
        "final_prd": None,
        "errors": [],
        "logs": [],
    }
    state.update(overrides)
    return state


def patch_genai_client(monkeypatch, module_path, response_text):
    response = MagicMock()
    response.text = response_text

    models = MagicMock()
    models.generate_content.return_value = response

    client = MagicMock()
    client.models = models

    monkeypatch.setattr(
        f"{module_path}.genai.Client",
        lambda api_key: client,
    )
    return client


def test_planner_agent_writes_output_and_log(monkeypatch):
    client = patch_genai_client(
        monkeypatch,
        "app.agents.planner",
        "Validated planning output",
    )
    state = make_agent_state(planner_output="")

    result = PlannerAgent(api_key="test-api-key", model_name="test-model").run(state)

    assert result["planner_output"] == "Validated planning output"
    assert result["logs"] == ["Planner → completed"]
    assert result["errors"] == []

    client.models.generate_content.assert_called_once()
    call_kwargs = client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert state["product_idea"] in call_kwargs["contents"]


def test_business_analyst_agent_formats_retrieved_context(monkeypatch):
    client = patch_genai_client(
        monkeypatch,
        "app.agents.business_analyst",
        "Business analyst output",
    )
    retriever = MagicMock()
    retriever.retrieve_relevant_knowledge.return_value = [
        {
            "text": "Interview students before defining tutor matching requirements.",
            "metadata": {
                "title": "Discovery Guide",
                "source": "discovery.md",
            },
        }
    ]
    state = make_agent_state(retrieved_context="")

    result = BusinessAnalystAgent(
        api_key="test-api-key",
        model_name="test-model",
        retriever=retriever,
    ).run(state)

    expected_context = (
        "From Document 'Discovery Guide' (Source: discovery.md):\n"
        "Interview students before defining tutor matching requirements."
    )
    assert result["retrieved_context"] == expected_context
    assert result["business_analyst_output"] == "Business analyst output"
    assert result["logs"] == ["Business Analyst -> completed"]
    assert result["errors"] == []

    retriever.retrieve_relevant_knowledge.assert_called_once_with(state["product_idea"])
    call_kwargs = client.models.generate_content.call_args.kwargs
    assert expected_context in call_kwargs["contents"]
    assert state["planner_output"] in call_kwargs["contents"]


def test_product_manager_agent_uses_business_analysis_and_context(monkeypatch):
    client = patch_genai_client(
        monkeypatch,
        "app.agents.product_manager",
        "Product manager output",
    )
    state = make_agent_state(
        business_analyst_output="Specific BA findings",
        retrieved_context="Specific retrieved product knowledge",
        product_manager_output="",
    )

    result = ProductManagerAgent(api_key="test-api-key", model_name="test-model").run(state)

    assert result["product_manager_output"] == "Product manager output"
    assert result["logs"] == ["Product Manager → completed"]
    assert result["errors"] == []

    call_kwargs = client.models.generate_content.call_args.kwargs
    assert "Specific BA findings" in call_kwargs["contents"]
    assert "Specific retrieved product knowledge" in call_kwargs["contents"]


def test_prd_generator_agent_validates_final_prd(monkeypatch):
    client = patch_genai_client(
        monkeypatch,
        "app.agents.prd_generator",
        json.dumps(SAMPLE_PRD),
    )
    state = make_agent_state(final_prd=None)

    result = PRDGeneratorAgent(api_key="test-api-key", model_name="test-model").run(state)

    assert isinstance(result["final_prd"], PRDDocument)
    assert result["final_prd"].product_overview == SAMPLE_PRD["product_overview"]
    assert result["logs"] == ["PRD Generator → completed"]
    assert result["errors"] == []

    call_kwargs = client.models.generate_content.call_args.kwargs
    assert state["planner_output"] in call_kwargs["contents"]
    assert state["business_analyst_output"] in call_kwargs["contents"]
    assert state["product_manager_output"] in call_kwargs["contents"]