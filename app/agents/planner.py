"""Planner Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings


class PlannerAgent:
    """Analyzes the initial product idea and identifies discovery areas."""

    def __init__(self, api_key: str = "", model_name: str = ""):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model

    def run(self, state: AgentState) -> AgentState:
        """Execute the Planner Agent."""

        print("Planner Agent starting...")

        product_idea = state.get("product_idea", "")

        if not product_idea:
            state["errors"].append(
                "Planner Agent: No product idea provided."
            )
            return state

        if not self.api_key:
            state["errors"].append(
                "Planner Agent: Gemini API key is missing."
            )
            return state

        prompt = f"""
You are a professional Product Planner.

Analyze the following product idea.

Product Idea:
{product_idea}

Identify:

1. Core value proposition and what makes the product useful.
2. Key user and business questions that should be validated.
3. Important product assumptions.
4. Potential target audience segments.
5. Essential product discovery areas.
6. Important scope considerations for an MVP.

Do not generate a complete PRD.

Produce structured planning and discovery information that can
be passed to a Business Analyst Agent.
"""

        try:
            client = genai.Client(api_key=self.api_key)

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )

            output = getattr(response, "text", "") or ""

            if not output.strip():
                state["errors"].append(
                    "Planner Agent returned an empty response."
                )
                return state

            state["planner_output"] = output
            state["logs"].append("Planner Agent -> completed")

            print("Planner Agent completed.")

        except Exception as exc:
            state["errors"].append(
                f"Planner Agent execution failed: {exc}"
            )

        return state