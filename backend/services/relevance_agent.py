from backend.utils.embedding_model import get_embedding_model
from backend.utils.similarity import calculate_similarity, normalize_score
from backend.utils.keyword_utils import keyword_coverage
from backend.utils.reason_generator import generate_relevance_reason

class RelevanceJudgeAgent:

    @staticmethod
    def evaluate(question, response, retrieved_docs):

        import re
        q_clean = question.lower().strip()
        r_clean = response.lower().strip()

        # Math / Arithmetic relevance check
        math_match = re.search(r"(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)", q_clean)
        if math_match:
            n1 = float(math_match.group(1))
            op = math_match.group(2)
            n2 = float(math_match.group(3))
            expected = None
            if op == '+': expected = n1 + n2
            elif op == '-': expected = n1 - n2
            elif op == '*': expected = n1 * n2
            elif op == '/' and n2 != 0: expected = n1 / n2

            if expected is not None:
                exp_str = str(int(expected)) if expected.is_integer() else str(round(expected, 4))
                if exp_str in r_clean or exp_str in re.findall(r"-?\d+(?:\.\d+)?", r_clean):
                    return {
                        "relevance_score": 100.0,
                        "relevance_level": "Highly Relevant",
                        "confidence": "Very High",
                        "semantic_similarity": 100.0,
                        "keyword_coverage": 100.0,
                        "context_alignment": 100.0,
                        "completeness": 100.0,
                        "reason": "The response directly and accurately answers the arithmetic question."
                    }

        model = get_embedding_model()

        # 1. Semantic similarity
        q_embedding = model.encode(question)
        r_embedding = model.encode(response)

        semantic_similarity = calculate_similarity(q_embedding, r_embedding)
        semantic_score = normalize_score(semantic_similarity)

        # 2. Keyword coverage
        keyword_score = keyword_coverage(question, response)

        # 3. Context alignment & Weighted Score
        context_text = " ".join([doc.get("context", "") for doc in retrieved_docs if isinstance(doc, dict)])

        if context_text.strip():
            c_embedding = model.encode(context_text)
            context_similarity = calculate_similarity(r_embedding, c_embedding)
            context_score = normalize_score(context_similarity)
            completeness_score = min(len(response.split()) / 20, 1.0) * 100

            final_score = (
                semantic_score * 0.4 +
                keyword_score * 0.3 +
                context_score * 0.2 +
                completeness_score * 0.1
            )
        else:
            context_score = 100.0
            completeness_score = 100.0 if len(response.strip()) > 0 else 0.0
            final_score = (
                semantic_score * 0.6 +
                keyword_score * 0.4
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