"""Tests for the multi-agent LangGraph workflow."""

from app.agents.graph import build_agent_graph


def test_multi_agent_workflow_runs_in_correct_order(monkeypatch):
    execution_order = []

    class FakePlanner:
        def run(self, state):
            execution_order.append("planner")
            state["planner_output"] = "Planner completed"
            state["logs"].append("Planner → completed")
            return state

    class FakeBusinessAnalyst:
        def run(self, state):
            execution_order.append("business_analyst")
            assert state["planner_output"] == "Planner completed"
            state["business_analyst_output"] = "Business analysis completed"
            state["logs"].append("Business Analyst → completed")
            return state

    class FakeProductManager:
        def run(self, state):
            execution_order.append("product_manager")
            assert state["business_analyst_output"] == "Business analysis completed"
            state["product_manager_output"] = "Product requirements completed"
            state["logs"].append("Product Manager → completed")
            return state

    class FakePRDGenerator:
        def run(self, state):
            execution_order.append("prd_generator")
            assert state["product_manager_output"] == "Product requirements completed"
            state["final_prd"] = {"status": "generated"}
            state["logs"].append("PRD Generator → completed")
            return state

    monkeypatch.setattr(
        "app.agents.graph.PlannerAgent",
        FakePlanner,
    )
    monkeypatch.setattr(
        "app.agents.graph.BusinessAnalystAgent",
        FakeBusinessAnalyst,
    )
    monkeypatch.setattr(
        "app.agents.graph.ProductManagerAgent",
        FakeProductManager,
    )
    monkeypatch.setattr(
        "app.agents.graph.PRDGeneratorAgent",
        FakePRDGenerator,
    )

    graph = build_agent_graph()

    initial_state = {
        "product_idea": "An app where college students can find tutors.",
        "retrieved_context": "",
        "planner_output": "",
        "business_analyst_output": "",
        "product_manager_output": "",
        "final_prd": None,
        "errors": [],
        "logs": [],
    }

    result = graph.invoke(initial_state)

    assert execution_order == [
        "planner",
        "business_analyst",
        "product_manager",
        "prd_generator",
    ]

    assert result["planner_output"] == "Planner completed"
    assert result["business_analyst_output"] == "Business analysis completed"
    assert result["product_manager_output"] == "Product requirements completed"
    assert result["final_prd"] == {"status": "generated"}

    assert not result["errors"]