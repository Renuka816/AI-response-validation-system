from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# --------------------------------------------------
# Load Model (Loads only once)
# --------------------------------------------------

from backend.services.embedding_service import EmbeddingService

model = EmbeddingService.get_model()


# --------------------------------------------------
# Knowledge Agent
# --------------------------------------------------

class KnowledgeAgent:

    @staticmethod
    def evaluate(ai_response: str, retrieved_documents: list):

        """
        Parameters
        ----------
        ai_response : str
            AI generated answer.

        retrieved_documents : list
            Output from rag_service.retrieve_documents()

        Returns
        -------
        dict
        """

        if not retrieved_documents:

            return {
                "knowledge_score": 0,
                "confidence": 0,
                "best_matching_context": "",
                "reason": "No supporting knowledge found."
            }

        # ------------------------------------------
        # Embed AI Response
        # ------------------------------------------

        response_embedding = model.encode(ai_response)

        similarities = []

        # ------------------------------------------
        # Compare with each retrieved document
        # ------------------------------------------

        for document in retrieved_documents:

            context = document["context"]

            context_embedding = model.encode(context)

            similarity = cosine_similarity(
                [response_embedding],
                [context_embedding]
            )[0][0]

            similarities.append((similarity, context))

        # ------------------------------------------
        # Best Matching Context
        # ------------------------------------------

        best_similarity, best_context = max(
            similarities,
            key=lambda x: x[0]
        )

        # ------------------------------------------
        # Convert similarity to percentage
        # ------------------------------------------

        knowledge_score = round(best_similarity * 100, 2)

        knowledge_score = max(
            0,
            min(100, knowledge_score)
        )

        # ------------------------------------------
        # Confidence
        # ------------------------------------------

        if knowledge_score >= 85:

            confidence = "High"

        elif knowledge_score >= 60:

            confidence = "Medium"

        else:

            confidence = "Low"

        # ------------------------------------------
        # Return Result
        # ------------------------------------------

        return {

            "knowledge_score": knowledge_score,

            "confidence": confidence,

            "best_matching_context": best_context,

            "reason": (
                "Knowledge score calculated using "
                "semantic similarity between "
                "AI response and retrieved evidence."
            )

        }