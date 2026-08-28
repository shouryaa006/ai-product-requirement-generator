"""Product Manager Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings


class ProductManagerAgent:
    """Translates business analysis into actionable product requirements."""

    def __init__(
        self,
        api_key: str = "",
        model_name: str = "",
    ):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model

    def run(self, state: AgentState) -> AgentState:
        """Execute the Product Manager Agent."""

        print("Product Manager Agent starting...")

        product_idea = state.get("product_idea", "")
        ba_output = state.get("business_analyst_output", "")
        retrieved_context = state.get("retrieved_context", "")

        if not product_idea:
            state["errors"].append(
                "Product Manager Agent: No product idea provided."
            )
            return state

        if not self.api_key:
            state["errors"].append(
                "Product Manager Agent: Gemini API key is missing."
            )
            return state

        prompt = f"""
You are a professional Product Manager.

Translate the product concept and Business Analyst findings
into clear, actionable product requirements.

PRODUCT IDEA:

{product_idea}

BUSINESS ANALYST REPORT:

{ba_output}

RETRIEVED PRODUCT KNOWLEDGE:

{
    retrieved_context
    if retrieved_context
    else "No specific retrieved reference context available."
}

Your tasks:

1. Define detailed functional requirements.
2. Define meaningful non-functional requirements.
3. Write specific and realistic user stories.
4. Establish business objectives and measurable KPIs.
5. Define MVP scope.
6. Define post-MVP enhancements.
7. Identify assumptions.
8. Identify risks and mitigation considerations.
9. Ensure requirements are concrete and testable.

Guidelines:

- Build upon the Business Analyst's findings.
- Use retrieved knowledge where relevant.
- Do not generate the final PRD JSON.
- Do not write vague requirements.
- Produce a structured professional product-management analysis.
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
                    "Product Manager Agent returned an empty response."
                )
                return state

            state["product_manager_output"] = output
            state["logs"].append(
                "Product Manager Agent -> completed"
            )

            print("Product Manager Agent completed.")

        except Exception as exc:
            state["errors"].append(
                "Product Manager Agent execution failed: "
                f"{exc}"
            )

        return state