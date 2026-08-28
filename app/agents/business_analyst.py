"""Business Analyst Agent implementation."""

from google import genai
from google.genai import types

from app.agents.state import AgentState
from app.core.config import settings
from app.rag.retriever import get_retrieval_service


class BusinessAnalystAgent:
    """
    Analyzes business context, user problems, objectives,
    assumptions, risks, and relevant product knowledge.
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
            print(
                f"Business Analyst Agent: "
                f"RAG initialization warning: {exc}"
            )

    def run(self, state: AgentState) -> AgentState:
        """Execute the Business Analyst Agent."""

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

        # Retrieve relevant knowledge through the existing RAG system.
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
                            f"{result.get('text', '')}"
                        )

                    retrieved_context = "\n\n---\n\n".join(
                        context_parts
                    )

                    state["retrieved_context"] = retrieved_context

            except Exception as exc:
                print(
                    f"Business Analyst Agent RAG retrieval failed: {exc}"
                )

                state["errors"].append(
                    f"Business Analyst Agent RAG retrieval failed: {exc}"
                )

                # Continue without retrieved context.
                retrieved_context = ""

        prompt = f"""
You are a professional Business Analyst.

Analyze the product idea using the Planner Agent's discovery
analysis and the available product-management knowledge.

PRODUCT IDEA:

{product_idea}

PLANNER AGENT ANALYSIS:

{planner_output}

RETRIEVED PRODUCT KNOWLEDGE:

{
    retrieved_context
    if retrieved_context
    else "No specific retrieved reference context available."
}

Your tasks:

1. Define the core user problem.
2. Define the business problem.
3. Identify primary user segments.
4. Identify user pain points, needs, goals, and motivations.
5. Identify business objectives.
6. Suggest measurable success metrics.
7. Identify important assumptions.
8. Identify critical product and business risks.
9. Identify important discovery questions.

Guidelines:

- Use the Planner Agent analysis as an input.
- Use retrieved knowledge when relevant.
- Do not blindly copy retrieved information.
- Do not generate the final PRD.
- Do not generate PRD JSON.
- Produce a structured professional business analysis.
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
                    "Business Analyst Agent returned an empty response."
                )
                return state

            state["business_analyst_output"] = output
            state["logs"].append(
                "Business Analyst Agent -> completed"
            )

            print("Business Analyst Agent completed.")

        except Exception as exc:
            state["errors"].append(
                "Business Analyst Agent execution failed: "
                f"{exc}"
            )

        return state