from sklearn.metrics.pairwise import cosine_similarity
from backend.services.embedding_service import EmbeddingService

model = EmbeddingService.get_model()


class HallucinationAgent:

    @staticmethod
    def evaluate(ai_response: str, retrieved_documents: list):

        if not retrieved_documents:
            return {
                "hallucination_score": 100,
                "hallucinated": True,
                "status": "Hallucinated",
                "supported_claims": 0,
                "unsupported_claims": 1,
                "evidence": "No reference documents retrieved.",
                "reason": "No supporting evidence was retrieved."
            }

        response_embedding = model.encode(ai_response)

        similarities = []

        for document in retrieved_documents:

            context_embedding = model.encode(document["context"])

            similarity = cosine_similarity(
                [response_embedding],
                [context_embedding]
            )[0][0]

            similarities.append(similarity)

        best_similarity = max(similarities)

        hallucination_score = round((1 - best_similarity) * 100, 2)
        hallucination_score = max(0, min(100, hallucination_score))

        # ---------- Extra Details ----------
        if hallucination_score < 20:
            status = "Well Supported"
            supported_claims = 5
            unsupported_claims = 0

        elif hallucination_score < 40:
            status = "Mostly Supported"
            supported_claims = 4
            unsupported_claims = 1

        elif hallucination_score < 60:
            status = "Partially Supported"
            supported_claims = 3
            unsupported_claims = 2

        else:
            status = "Hallucinated"
            supported_claims = 1
            unsupported_claims = 4

        evidence = f"Best semantic similarity with retrieved knowledge: {round(best_similarity * 100,2)}%"

        if hallucination_score > 40:
            hallucinated = True
            reason = "The response contains information weakly supported by the retrieved knowledge."
        else:
            hallucinated = False
            reason = "The response is largely supported by the retrieved knowledge."

        return {
            "hallucination_score": hallucination_score,
            "hallucinated": hallucinated,
            "status": status,
            "supported_claims": supported_claims,
            "unsupported_claims": unsupported_claims,
            "evidence": evidence,
            "reason": reason
        }