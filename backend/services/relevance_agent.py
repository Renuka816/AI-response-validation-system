from backend.utils.embedding_model import get_embedding_model
from backend.utils.similarity import calculate_similarity, normalize_score
from backend.utils.keyword_utils import keyword_coverage
from backend.utils.reason_generator import generate_relevance_reason

class RelevanceJudgeAgent:

    @staticmethod
    def evaluate(question, response, retrieved_docs):

        model = get_embedding_model()

        # 1. Semantic similarity
        q_embedding = model.encode(question)
        r_embedding = model.encode(response)

        semantic_similarity = calculate_similarity(q_embedding, r_embedding)
        semantic_score = normalize_score(semantic_similarity)

        # 2. Keyword coverage
        keyword_score = keyword_coverage(question, response)

        # 3. Context alignment
        context_text = " ".join([doc["context"] for doc in retrieved_docs])

        if context_text.strip():
            c_embedding = model.encode(context_text)
            context_similarity = calculate_similarity(r_embedding, c_embedding)
            context_score = normalize_score(context_similarity)
        else:
            context_score = 0

        # 4. Completeness
        completeness_score = min(len(response.split()) / 40, 1.0) * 100

        # 5. Weighted final score
        final_score = (
            semantic_score * 0.5 +
            keyword_score * 0.2 +
            context_score * 0.2 +
            completeness_score * 0.1
        )

        final_score = round(final_score, 2)

        # 6. Confidence
        if final_score >= 90:
            confidence = "Very High"
            level = "Highly Relevant"
        elif final_score >= 80:
            confidence = "High"
            level = "Highly Relevant"
        elif final_score >= 65:
            confidence = "Moderate"
            level = "Relevant"
        elif final_score >= 50:
            confidence = "Low"
            level = "Partially Relevant"
        else:
            confidence = "Very Low"
            level = "Irrelevant"

        # 7. Generate reason
        reason = generate_relevance_reason(
            final_score,
            keyword_score,
            context_score
        )

        return {
            "relevance_score": final_score,
            "relevance_level": level,
            "confidence": confidence,
            "semantic_similarity": round(semantic_score, 2),
            "keyword_coverage": round(keyword_score, 2),
            "context_alignment": round(context_score, 2),
            "completeness": round(completeness_score, 2),
            "reason": reason
        }