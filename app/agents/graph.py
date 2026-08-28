"""LangGraph orchestrator for the multi-agent PRD workflow."""

from langgraph.graph import END, START, StateGraph

from app.agents.business_analyst import BusinessAnalystAgent
from app.agents.planner import PlannerAgent
from app.agents.prd_generator import PRDGeneratorAgent
from app.agents.product_manager import ProductManagerAgent
from app.agents.state import AgentState


def build_agent_graph():
    """Build and compile the deterministic PRD generation workflow."""

    workflow = StateGraph(AgentState)

    # Initialize agents
    planner = PlannerAgent()
    business_analyst = BusinessAnalystAgent()
    product_manager = ProductManagerAgent()
    prd_generator = PRDGeneratorAgent()

    # Register workflow nodes
    workflow.add_node("planner", planner.run)
    workflow.add_node("business_analyst", business_analyst.run)
    workflow.add_node("product_manager", product_manager.run)
    workflow.add_node("prd_generator", prd_generator.run)

    # Deterministic workflow
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "business_analyst")
    workflow.add_edge("business_analyst", "product_manager")
    workflow.add_edge("product_manager", "prd_generator")
    workflow.add_edge("prd_generator", END)

    return workflow.compile()


# Compiled workflow used by the API
compiled_graph = build_agent_graph()