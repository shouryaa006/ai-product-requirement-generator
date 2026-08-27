"""Planner Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings


class PlannerAgent:
    """Planner Agent: Analyzes the initial product idea and identifies key discovery areas."""

    def __init__(self, api_key: str = "", model_name: str = ""):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model

    def run(self, state: AgentState) -> AgentState:
        """Executes the Planner Agent node."""
        print("Planner Agent starting...")
        product_idea = state.get("product_idea", "")

        if not product_idea:
            state["errors"].append("Planner Agent: No product idea provided.")
            return state

        if not self.api_key:
            state["errors"].append("Planner Agent: Gemini API key is missing.")
            return state

        client = genai.Client(api_key=self.api_key)

        prompt = f"""
You are a professional Product Planner.
Analyze the following product idea and identify:
1. Core value proposition and what makes it unique.
2. Key user/business questions and assumptions that must be validated during discovery.
3. Potential target audience segments and their main characteristics.
4. Essential initial product discovery steps before generating a PRD.

Product Idea:
{state["product_idea"]}

Write a detailed, structured, professional analysis as your output. Do NOT write a full PRD. Only produce structured planning and discovery information.
"""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )
            state["planner_output"] = getattr(response, "text", "") or ""
            state["logs"].append("Planner → completed")
        except Exception as exc:
            state["errors"].append(f"Planner Agent execution failed: {exc}")

        return state
