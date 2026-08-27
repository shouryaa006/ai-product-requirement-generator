"""LangGraph orchestrator and workflow compilation."""

from langgraph.graph import END, START, StateGraph

from app.agents.business_analyst import BusinessAnalystAgent
from app.agents.planner import PlannerAgent
from app.agents.prd_generator import PRDGeneratorAgent
from app.agents.product_manager import ProductManagerAgent
from app.agents.state import AgentState


def build_agent_graph() -> StateGraph:
    """Builds and compiles the deterministic multi-agent workflow graph."""
    workflow = StateGraph(AgentState)

    # Initialize agents
    planner = PlannerAgent()
    business_analyst = BusinessAnalystAgent()
    product_manager = ProductManagerAgent()
    prd_generator = PRDGeneratorAgent()

    # Define nodes
    workflow.add_node("planner", planner.run)
    workflow.add_node("business_analyst", business_analyst.run)
    workflow.add_node("product_manager", product_manager.run)
    workflow.add_node("prd_generator", prd_generator.run)

    # Define edges (Deterministic sequential order)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "business_analyst")
    workflow.add_edge("business_analyst", "product_manager")
    workflow.add_edge("product_manager", "prd_generator")
    workflow.add_edge("prd_generator", END)

    return workflow.compile()


# Singleton compiled graph instance
compiled_graph = build_agent_graph()
