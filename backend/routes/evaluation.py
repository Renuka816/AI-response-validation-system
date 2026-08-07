from fastapi import APIRouter

router = APIRouter()

from backend.models.request_model import EvaluationRequest
from backend.services.evaluation_service import EvaluationService

@router.post("/evaluate")
async def evaluate_response(request: EvaluationRequest):
    """
    Evaluate an AI-generated response using
    the RAG-based multi-agent evaluation pipeline.
    """

    result = EvaluationService.process_request(request)

    return {
        "status": "success",
        "message": "Evaluation completed successfully.",
        "data": result
    }