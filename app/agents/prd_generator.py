"""PRD Generator Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings
from app.schemas.prd import PRDDocument
from app.services.llm import parse_prd_response
from app.services.prompts import SYSTEM_PROMPT


class PRDGeneratorAgent:
    """
    Generates the final validated PRD using the outputs
    of the Planner, Business Analyst, and Product Manager agents.
    """

    def __init__(
        self,
        api_key: str = "",
        model_name: str = "",
    ):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model

    def run(self, state: AgentState) -> AgentState:
        """Execute the final PRD Generator Agent."""

        print("PRD Generator Agent starting...")

        product_idea = state.get("product_idea", "")
        planner_output = state.get("planner_output", "")
        ba_output = state.get("business_analyst_output", "")
        pm_output = state.get("product_manager_output", "")
        retrieved_context = state.get("retrieved_context", "")

        if not product_idea:
            state["errors"].append(
                "PRD Generator Agent: No product idea provided."
            )
            return state

        if not self.api_key:
            state["errors"].append(
                "PRD Generator Agent: Gemini API key is missing."
            )
            return state

        user_prompt = f"""
You are a professional Product Requirements Analyst.

Create the final Product Requirements Document by synthesizing
all previous agent outputs.

ORIGINAL PRODUCT IDEA:

{product_idea}

PLANNER AGENT:

{planner_output}

BUSINESS ANALYST AGENT:

{ba_output}

PRODUCT MANAGER AGENT:

{pm_output}

RAG KNOWLEDGE:

{
    retrieved_context
    if retrieved_context
    else "No specific retrieved reference context available."
}

Instructions:

1. Synthesize the findings into one comprehensive PRD.
2. Follow the exact PRD schema provided by the system instructions.
3. Preserve important insights from the previous agents.
4. Use RAG knowledge when relevant.
5. Do not blindly copy retrieved text.
6. Generate valid sequential IDs.
7. Ensure every required field is present.
8. Ensure the final response is valid JSON only.
9. Do not include Markdown.
10. Do not include explanations outside the JSON.
"""

        try:
            client = genai.Client(api_key=self.api_key)

            response = client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                    response_mime_type="application/json",
                    response_schema=PRDDocument,
                ),
            )

            raw_content = getattr(response, "text", "") or ""

            if not raw_content.strip():
                state["errors"].append(
                    "PRD Generator Agent returned an empty response."
                )
                return state

            final_prd = parse_prd_response(raw_content)

            state["final_prd"] = final_prd
            state["logs"].append(
                "PRD Generator Agent -> completed"
            )

            print("PRD Generator Agent completed.")

        except Exception as exc:
            state["errors"].append(
                "PRD Generator Agent execution failed: "
                f"{exc}"
            )

        return state