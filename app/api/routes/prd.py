"""PRD generation endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.prd import PRDDocument, PRDGenerateRequest
from app.agents.graph import compiled_graph

router = APIRouter(
    prefix="/api/v1/prd",
    tags=["prd"],
)


@router.post("/generate", response_model=PRDDocument)
def generate_prd(payload: PRDGenerateRequest) -> PRDDocument:
    """Generate a PRD using the LangGraph multi-agent workflow."""

    initial_state = {
        "product_idea": payload.product_idea,
        "retrieved_context": "",
        "planner_output": "",
        "business_analyst_output": "",
        "product_manager_output": "",
        "final_prd": None,
        "errors": [],
        "logs": [],
    }

    print("\n" + "=" * 60)
    print("STARTING MULTI-AGENT PRD WORKFLOW")
    print("=" * 60)
    print(f"Product idea: {payload.product_idea}")

    try:
        final_state = compiled_graph.invoke(initial_state)

        print("\n--- AGENT LOGS ---")
        for log in final_state.get("logs", []):
            print(log)

        print("\n--- AGENT ERRORS ---")
        for error in final_state.get("errors", []):
            print(error)

        print("\n--- WORKFLOW RESULT ---")
        print(
            f"Final PRD exists: "
            f"{final_state.get('final_prd') is not None}"
        )

        errors = final_state.get("errors", [])

        if errors:
            print("\nWORKFLOW FAILED:")
            for error in errors:
                print(f"  ERROR: {error}")

            raise HTTPException(
                status_code=502,
                detail=errors[-1],
            )

        final_prd = final_state.get("final_prd")

        if final_prd is None:
            print("ERROR: Workflow completed without a final PRD.")

            raise HTTPException(
                status_code=502,
                detail="The agent workflow completed without generating a PRD.",
            )

        print("\nMULTI-AGENT WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)

        return final_prd

    except HTTPException:
        raise

    except Exception as exc:
        print("\n" + "=" * 60)
        print("UNEXPECTED WORKFLOW ERROR")
        print("=" * 60)
        print(f"{type(exc).__name__}: {exc}")

        raise HTTPException(
            status_code=502,
            detail="PRD generation failed. Please check the backend terminal.",
        ) from None