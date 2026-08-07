from fastapi import APIRouter, UploadFile, File
from backend.models.request_model import EvaluationRequest
from backend.services.evaluation_service import EvaluationService

import pandas as pd
import io

router = APIRouter()


@router.post("/batch-evaluate")
async def batch_evaluate(file: UploadFile = File(...)):

    # Read uploaded CSV
    contents = await file.read()

    df = pd.read_csv(
        io.StringIO(contents.decode("utf-8"))
    )

    results = []
    total_score = 0

    for _, row in df.iterrows():

        # Accept both "question" and "Question"
        question = row.get("question", row.get("Question"))

        # Accept both "response" and "Response"
        response = row.get("response", row.get("Response"))

        request = EvaluationRequest(
            question=question,
            response=response,
            reference_answer="",
            source_document=""
        )

        evaluation = EvaluationService.process_request(request)

        final_score = evaluation["final_result"]["final_score"]

        total_score += final_score

        results.append({

            "question": question,

            "response": response,

            "knowledge_score":
                evaluation["knowledge"]["knowledge_score"],

            "relevance_score":
                evaluation["relevance"]["relevance_score"],

            "hallucination_score":
                evaluation["hallucination"]["hallucination_score"],

            "completeness_score":
                evaluation["completeness"]["completeness_score"],

            "final_score":
                final_score,

            "grade":
                evaluation["final_result"]["grade"],

            "reason":
                evaluation["final_result"]["reason"]

        })

    average_score = round(
        total_score / len(results),
        2
    ) if results else 0

    return {

        "success": True,

        "total_records": len(results),

        "average_score": average_score,

        "results": results

    }