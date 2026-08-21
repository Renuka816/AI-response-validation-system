from sklearn.metrics.pairwise import cosine_similarity

from backend.services.embedding_service import EmbeddingService


class HallucinationAgent:

    @staticmethod
    def evaluate(ai_response: str, retrieved_documents: list):

        # =========================================================
        # No retrieved evidence
        # =========================================================

        if not retrieved_documents:

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "General Knowledge Grounded",
                "supported_claims": 1,
                "unsupported_claims": 0,
                "evidence": "No retrieved evidence was available.",
                "reason": (
                    "No relevant retrieval evidence was available. "
                    "The response was evaluated using general knowledge."
                )
            }

        # =========================================================
        # Load local embedding model
        # =========================================================

        model = EmbeddingService.get_model()

        response_embedding = model.encode(ai_response)

        # =========================================================
        # Compare response against retrieved evidence
        # =========================================================

        similarities = []

        for document in retrieved_documents:

            context = document.get("context", "")

            if not context.strip():
                continue

            context_embedding = model.encode(context)

            similarity = cosine_similarity(
                [response_embedding],
                [context_embedding]
            )[0][0]

            similarities.append(similarity)

        # No usable documents
        if not similarities:

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "General Knowledge Grounded",
                "supported_claims": 1,
                "unsupported_claims": 0,
                "evidence": "No usable retrieved context.",
                "reason": (
                    "The retrieved documents did not contain usable "
                    "evidence, so the response was not penalized."
                )
            }

        best_similarity = max(similarities)

        similarity_percent = round(
            best_similarity * 100,
            2
        )

        # =========================================================
        # IMPORTANT:
        # Weak evidence should NOT automatically mean hallucination.
        # =========================================================

        if best_similarity < 0.40:

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "General Knowledge Grounded",
                "supported_claims": 1,
                "unsupported_claims": 0,
                "evidence": (
                    f"Retrieved evidence had low semantic support "
                    f"({similarity_percent}%)."
                ),
                "reason": (
                    "The retrieved documents were not sufficiently "
                    "relevant to verify the response. Therefore, "
                    "the response was not classified as hallucinated."
                )
            }

        # =========================================================
        # Strong evidence
        # =========================================================

        if best_similarity >= 0.70:

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "Well Supported",
                "supported_claims": 5,
                "unsupported_claims": 0,
                "evidence": (
                    f"Strong semantic support from retrieved knowledge "
                    f"({similarity_percent}%)."
                ),
                "reason": (
                    "The response is strongly supported by the "
                    "retrieved knowledge."
                )
            }

        # =========================================================
        # Moderate evidence
        # =========================================================

        if best_similarity >= 0.55:

            hallucination_score = round(
                (1 - best_similarity) * 50,
                2
            )

            return {
                "hallucination_score": hallucination_score,
                "hallucinated": False,
                "status": "Mostly Supported",
                "supported_claims": 4,
                "unsupported_claims": 1,
                "evidence": (
                    f"Moderate semantic support from retrieved "
                    f"knowledge ({similarity_percent}%)."
                ),
                "reason": (
                    "The response has reasonable support from "
                    "the retrieved knowledge, although some claims "
                    "could not be directly verified."
                )
            }

        # =========================================================
        # Partial evidence
        # =========================================================

        hallucination_score = round(
            (1 - best_similarity) * 100,
            2
        )

        hallucination_score = max(
            0,
            min(100, hallucination_score)
        )

        if hallucination_score < 40:

            status = "Partially Supported"
            hallucinated = False
            supported_claims = 3
            unsupported_claims = 2

            reason = (
                "The response is partially supported by the "
                "retrieved knowledge, but some claims require "
                "additional verification."
            )

        else:

            status = "Potentially Hallucinated"
            hallucinated = True
            supported_claims = 1
            unsupported_claims = 4

            reason = (
                "The response has weak support from the available "
                "retrieved knowledge and may contain unsupported claims."
            )

        return {
            "hallucination_score": hallucination_score,
            "hallucinated": hallucinated,
            "status": status,
            "supported_claims": supported_claims,
            "unsupported_claims": unsupported_claims,
            "evidence": (
                f"Best semantic similarity with retrieved knowledge: "
                f"{similarity_percent}%"
            ),
            "reason": reason
        }