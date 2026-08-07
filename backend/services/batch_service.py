import pandas as pd
from io import StringIO

from backend.models.request_model import EvaluationRequest
from backend.services.evaluation_service import EvaluationService


class BatchService:

    @staticmethod
    async def evaluate_csv(file):

        contents = await file.read()

        csv_data = StringIO(contents.decode("utf-8"))

        df = pd.read_csv(csv_data)

        results = []

        for _, row in df.iterrows():

            request = EvaluationRequest(

                question=str(row["Question"]),
                response=str(row["Response"]),
                reference_answer="",
                source_document=""

            )

            evaluation = EvaluationService.process_request(request)

            results.append({

                "question": row["Question"],

                "knowledge": evaluation["knowledge"]["knowledge_score"],

                "relevance": evaluation["relevance"]["relevance_score"],

                "hallucination": evaluation["hallucination"]["hallucination_score"],

                "completeness": evaluation["completeness"]["completeness_score"],

                "final_score": evaluation["final_result"]["final_score"],

                "grade": evaluation["final_result"]["grade"]

            })

        return results