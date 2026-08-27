"""Product Manager Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings


class ProductManagerAgent:
    """Product Manager Agent: Translates business analysis into product requirements."""

    def __init__(self, api_key: str = "", model_name: str = ""):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model

    def run(self, state: AgentState) -> AgentState:
        """Executes the Product Manager Agent node."""
        print("Product Manager Agent starting...")
        product_idea = state.get("product_idea", "")
        ba_output = state.get("business_analyst_output", "")
        retrieved_context = state.get("retrieved_context", "")

        if not product_idea:
            state["errors"].append("Product Manager Agent: No product idea provided.")
            return state

        if not self.api_key:
            state["errors"].append("Product Manager Agent: Gemini API key is missing.")
            return state

        client = genai.Client(api_key=self.api_key)

        prompt = f"""
You are a professional Product Manager.
Your job is to translate the following product idea, business analysis, and retrieved product knowledge into clear, actionable, structured product requirements.

Product Idea:
{product_idea}

Business Analysis (from Business Analyst Agent):
{ba_output}

Retrieved Product Management Knowledge (RAG):
{retrieved_context if retrieved_context else "No specific retrieved reference context available."}

Your tasks:
1. Identify detailed functional requirements (what the system must do).
2. Identify non-functional requirements (quality attributes, security, performance, etc.).
3. Write high-quality user stories (using the "As a... I want... so that..." format) with clear acceptance criteria.
4. Establish clear business objectives and product metrics/KPIs.
5. Define MVP (Minimum Viable Product) scope vs. post-MVP future enhancements.
6. Call out key assumptions and risks with mitigation strategies.

Guidelines:
- Ground your decisions using the retrieved product management knowledge where relevant.
- Do NOT generate the final PRD JSON.
- Provide a clear, highly structured and professional requirements document in text format.
"""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )
            state["product_manager_output"] = getattr(response, "text", "") or ""
            state["logs"].append("Product Manager → completed")
        except Exception as exc:
            state["errors"].append(f"Product Manager Agent execution failed: {exc}")

        return state
