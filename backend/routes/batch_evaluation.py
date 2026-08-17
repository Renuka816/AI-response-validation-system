from fastapi import APIRouter, UploadFile, File
from backend.models.request_model import EvaluationRequest
from backend.services.evaluation_service import EvaluationService
from backend.database.database import save_evaluation

import pandas as pd
import io

router = APIRouter()


@router.post("/batch-evaluate")
async def batch_evaluate(file: UploadFile = File(...)):

    # -----------------------------------------
    # Read uploaded CSV
    # -----------------------------------------
    contents = await file.read()

    df = pd.read_csv(
        io.StringIO(contents.decode("utf-8"))
    )

    results = []
    total_score = 0

    # -----------------------------------------
    # Evaluate Each Record
    # -----------------------------------------
    for _, row in df.iterrows():

        # Accept both "question" and "Question"
        question = row.get(
            "question",
            row.get("Question")
        )

        # Accept both "response" and "Response"
        response = row.get(
            "response",
            row.get("Response")
        )

        # Accept model and dataset if present in row or file
        row_model = str(row.get("model", row.get("Model", "GPT-4o"))) if pd.notna(row.get("model", row.get("Model"))) else "GPT-4o"
        row_dataset = str(row.get("dataset", row.get("Dataset", file.filename or "Batch CSV"))) if pd.notna(row.get("dataset", row.get("Dataset"))) else (file.filename or "Batch CSV")

        # Create evaluation request
        request = EvaluationRequest(
            question=question,
            response=response,
            reference_answer="",
            source_document="",
            model=row_model,
            dataset=row_dataset
        )

        # Run complete evaluation
        evaluation = EvaluationService.process_request(
            request
        )

        # -----------------------------------------
        # Final Score
        # -----------------------------------------
        final_score = evaluation["final_result"]["final_score"]

        total_score += final_score

        # ---------------------------------------------------------
        # Save Batch Evaluation to Dashboard Database
        # ---------------------------------------------------------

        save_evaluation(

        question=question,

        response=response,

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

        evaluation_mode="batch",

        model=row_model,

        dataset=row_dataset

    )

        # -----------------------------------------
        # Store Evaluation Result
        # -----------------------------------------
        
        
        

        results.append({

            "question": question,

            "response": response,

            # Accuracy
            "accuracy_score":
                evaluation["accuracy"]["accuracy_score"],

            # Relevance
            "relevance_score":
                evaluation["relevance"]["relevance_score"],

            # Hallucination
            "hallucination_score":
                evaluation["hallucination"]["hallucination_score"],

            # Completeness
            "completeness_score":
                evaluation["completeness"]["completeness_score"],

            # Final score
            "final_score":
                final_score,

            # Grade
            "grade":
                evaluation["final_result"]["grade"],

            # Explanation
            "reason":
                evaluation["final_result"]["reason"]

        })

    # -----------------------------------------
    # Average Score
    # -----------------------------------------
    average_score = round(
        total_score / len(results),
        2
    ) if results else 0

    # -----------------------------------------
    # Return Batch Results
    # -----------------------------------------
    return {

        "success": True,

        "total_records": len(results),

        "average_score": average_score,

        "results": results

    }