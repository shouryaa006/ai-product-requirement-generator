"""Business Analyst Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings
from app.rag.retriever import get_retrieval_service


class BusinessAnalystAgent:
    """Business Analyst Agent.

    Analyzes the business context, problems, user pain points,
    objectives, assumptions, and risks.

    Reuses the existing RAG retrieval capability to ground its analysis.
    """

    def __init__(
        self,
        api_key: str = "",
        model_name: str = "",
        retriever=None,
    ):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model

        try:
            self.retriever = retriever or get_retrieval_service()
        except Exception as exc:
            self.retriever = None
            print(f"Business Analyst Agent: RAG initialization warning: {exc}")

    def run(self, state: AgentState) -> AgentState:
        """Execute the Business Analyst Agent node."""

        print("Business Analyst Agent starting...")

        product_idea = state.get("product_idea", "")
        planner_output = state.get("planner_output", "")
        retrieved_context = state.get("retrieved_context", "")

        if not product_idea:
            state["errors"].append(
                "Business Analyst Agent: No product idea provided."
            )
            return state

        if not self.api_key:
            state["errors"].append(
                "Business Analyst Agent: Gemini API key is missing."
            )
            return state

        # Reuse existing RAG retrieval if context has not already
        # been retrieved by an earlier workflow step.
        if not retrieved_context and self.retriever:
            try:
                results = self.retriever.retrieve_relevant_knowledge(
                    product_idea
                )

                if results:
                    context_parts = []

                    for result in results:
                        metadata = result.get("metadata", {})

                        source_title = metadata.get(
                            "title",
                            "Reference Document",
                        )
                        source_file = metadata.get(
                            "source",
                            "unknown",
                        )

                        context_parts.append(
                            f"From Document '{source_title}' "
                            f"(Source: {source_file}):\n"
                            f"{result['text']}"
                        )

                    retrieved_context = "\n\n---\n\n".join(
                        context_parts
                    )
                    state["retrieved_context"] = retrieved_context

            except Exception as exc:
                error_message = (
                    "Business Analyst Agent RAG retrieval failed: "
                    f"{exc}"
                )
                state["errors"].append(error_message)

                # Continue with the agent using the available context.
                retrieved_context = ""

        prompt = f"""
You are a professional Business Analyst.

Analyze the following product idea, initial discovery plan,
and available product-management knowledge.

Product Idea:
{product_idea}

Initial Discovery Plan from Planner Agent:
{planner_output}

Retrieved Product Management Knowledge:
{
    retrieved_context
    if retrieved_context
    else "No specific retrieved reference context available."
}

Your tasks:

1. Define the core user problem and business problem.
2. Identify the primary user segments and explain their key
   pain points, needs, goals, and motivations.
3. Identify the main business objectives and measurable
   success metrics.
4. Identify important product assumptions.
5. Identify critical business and product risks.
6. Explain any important discovery questions that should be
   validated before finalizing the product requirements.

Guidelines:

- Ground the analysis using the retrieved knowledge where relevant.
- Use the Planner Agent's output as an input to your analysis.
- Do not generate the final PRD.
- Do not generate final PRD JSON.
- Produce a detailed, structured, professional business analysis.
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

            state["business_analyst_output"] = (
                getattr(response, "text", "") or ""
            )

            state["logs"].append(
                "Business Analyst -> completed"
            )

        except Exception as exc:
            state["errors"].append(
                "Business Analyst Agent execution failed: "
                f"{exc}"
            )

        return state