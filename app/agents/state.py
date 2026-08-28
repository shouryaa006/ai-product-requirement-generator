"""Shared typed state definition for the LangGraph workflow."""

from typing import List, Optional, TypedDict

from app.schemas.prd import PRDDocument


class AgentState(TypedDict):
    """Shared state passed between all LangGraph agent nodes."""

    # Original user input
    product_idea: str

    # Knowledge retrieved from the RAG system
    retrieved_context: str

    # Intermediate agent outputs
    planner_output: str
    business_analyst_output: str
    product_manager_output: str

    # Final validated PRD
    final_prd: Optional[PRDDocument]

    # Workflow diagnostics
    errors: List[str]
    logs: List[str]