from fastapi import APIRouter

from backend.models.request_model import EvaluationRequest
from backend.services.evaluation_service import EvaluationService
from backend.database.database import save_evaluation

router = APIRouter()


@router.post("/evaluate")
async def evaluate_response(request: EvaluationRequest):
    """
    Evaluate an AI-generated response using
    the RAG-based multi-agent evaluation pipeline.
    """

    # -----------------------------------------
    # Run Evaluation
    # -----------------------------------------

    evaluation = EvaluationService.process_request(request)

    # -----------------------------------------
    # Extract Final Score
    # -----------------------------------------

    final_score = evaluation["final_result"]["final_score"]

    # -----------------------------------------
    # Save Evaluation to Dashboard Database
    # -----------------------------------------

    save_evaluation(

        question=request.question,

        response=request.response,

        accuracy_score=
            evaluation["accuracy"]["accuracy_score"],

        relevance_score=
            evaluation["relevance"]["relevance_score"],

        hallucination_score=
            evaluation["hallucination"]["hallucination_score"],

        completeness_score=
            evaluation["completeness"]["completeness_score"],

        final_score=final_score,

        grade=
            evaluation["final_result"]["grade"],

        timestamp=
            evaluation["timestamp"],

        evaluation_mode="single",

        model=request.model or "GPT-4o",

        dataset=request.dataset or "Single Query"
    )

    # -----------------------------------------
    # Return Existing Evaluation Result
    # -----------------------------------------

    return {
        "status": "success",
        "message": "Evaluation completed successfully.",
        "data": evaluation
    }