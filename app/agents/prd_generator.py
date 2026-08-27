"""PRD Generator Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings
from app.schemas.prd import PRDDocument
from app.services.llm import parse_prd_response
from app.services.prompts import SYSTEM_PROMPT


class PRDGeneratorAgent:
    """PRD Generator Agent: Consumes outputs from Planner, BA, and PM agents to generate the final validated PRD."""

    def __init__(self, api_key: str = "", model_name: str = ""):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model

    def run(self, state: AgentState) -> AgentState:
        """Executes the PRD Generator Agent node."""
        print("PRD Generator Agent starting...")
        product_idea = state.get("product_idea", "")
        planner_output = state.get("planner_output", "")
        ba_output = state.get("business_analyst_output", "")
        pm_output = state.get("product_manager_output", "")
        retrieved_context = state.get("retrieved_context", "")

        if not product_idea:
            state["errors"].append("PRD Generator Agent: No product idea provided.")
            return state

        if not self.api_key:
            state["errors"].append("PRD Generator Agent: Gemini API key is missing.")
            return state

        client = genai.Client(api_key=self.api_key)

        user_prompt = f"""
You are a professional Product Requirements Analyst.
Consolidate the product concept and intermediate agent analysis into a single, comprehensive, final Product Requirements Document (PRD) that conforms strictly to the requested schema.

ORIGINAL PRODUCT CONCEPT:
{product_idea}

PLANNING & DISCOVERY SCOPE (Planner Agent):
{planner_output}

BUSINESS ANALYST REPORT (BA Agent):
{ba_output}

DETAILED PRODUCT REQUIREMENTS (Product Manager Agent):
{pm_output}

GROUNDING KNOWLEDGE RETRIEVED (RAG):
{retrieved_context if retrieved_context else "No specific retrieved reference context available."}

INSTRUCTIONS:
1. Synthesize all the intermediate findings above into a singular, high-quality, professional PRD.
2. Adapt the guidance from the retrieved product management knowledge where relevant. Do not blindly copy text.
3. You must output a JSON object matching the requested schema.
4. No markdown, headings, bullet-prefix characters, or extra commentary before or after JSON.
"""

        try:
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
            # Reuse the existing parsing/validation method from Phase 2/3
            final_prd = parse_prd_response(raw_content)
            state["final_prd"] = final_prd
            state["logs"].append("PRD Generator → completed")
        except Exception as exc:
            state["errors"].append(f"PRD Generator Agent execution failed: {exc}")

        return state
