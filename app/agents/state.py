"""Shared typed state definition for the LangGraph workflow."""

from typing import Any, Dict, List, Optional, TypedDict

from app.schemas.prd import PRDDocument


class AgentState(TypedDict):
    """The shared state passed deterministically between LangGraph agent nodes."""

    # Input product idea
    product_idea: str

    # Context retrieved from local knowledge base
    retrieved_context: str

    # Agent outputs
    planner_output: str
    business_analyst_output: str
    product_manager_output: str

    # Final validated PRD Document
    final_prd: Optional[PRDDocument]

    # Error logging and agent execution status/messages
    errors: List[str]
    logs: List[str]
