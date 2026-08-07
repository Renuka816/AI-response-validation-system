class ScoringService:

    # ---------------------------------------
    # Recommendation (clean + useful)
    # ---------------------------------------
    @staticmethod
    def get_recommendation(score):

        if score >= 90:
            return "Excellent response. Accurate, complete, and highly reliable."

        elif score >= 75:
            return "Good response. Minor improvements in clarity or detail can enhance it."

        elif score >= 60:
            return "Decent response but lacks depth or clarity in some areas."

        elif score >= 40:
            return "Weak response. Needs better accuracy, structure, and completeness."

        else:
            return "Unreliable response. Contains major issues and should not be trusted."


    # ---------------------------------------
    # Hallucination Logic
    # ---------------------------------------
    @staticmethod
    def calculate_hallucination(knowledge, relevance):

        base = 100 - ((knowledge * 0.6) + (relevance * 0.4))

        return max(0, min(100, round(base, 2)))


    # ---------------------------------------
    # Reason Generator
    # ---------------------------------------
    @staticmethod
    def generate_reason(k, r, c, h, grade):

        strengths = []
        issues = []

        if k >= 70:
            strengths.append("strong subject understanding")
        if r >= 70:
            strengths.append("high relevance to the question")
        if c >= 70:
            strengths.append("good coverage of key points")
        if h <= 30:
            strengths.append("factually reliable")

        if k < 50:
            issues.append("lacks depth in concepts")
        if r < 60:
            issues.append("partially off-topic")
        if c < 60:
            issues.append("missing important details")
        if h > 50:
            issues.append("may contain incorrect information")

        result = ""

        if strengths:
            result += "The response shows " + ", ".join(strengths) + ". "

        if issues:
            result += "However, it " + ", ".join(issues) + ". "

        result += f"Overall quality is {grade}."

        return result


    # ---------------------------------------
    # FINAL SCORE CALCULATION (FULL FIX)
    # ---------------------------------------
    @staticmethod
    def calculate_final_score(knowledge, hallucination, relevance, completeness):

        w1 = 0.3   # knowledge
        w2 = 0.2   # hallucination
        w3 = 0.25  # relevance
        w4 = 0.25  # completeness

        # invert hallucination (lower hallucination = better)
        adjusted_hallucination = 100 - hallucination

        final_score = (
            knowledge * w1 +
            adjusted_hallucination * w2 +
            relevance * w3 +
            completeness * w4
        )

        # grade logic
        if final_score >= 85:
            grade = "Excellent"
        elif final_score >= 70:
            grade = "Good"
        elif final_score >= 50:
            grade = "Average"
        else:
            grade = "Poor"

        # ✅ ADD THESE (THIS FIXES YOUR UI ISSUE)
        recommendation = ScoringService.get_recommendation(final_score)

        reason = ScoringService.generate_reason(
            knowledge,
            relevance,
            completeness,
            hallucination,
            grade
        )

        return {
            "final_score": round(final_score, 2),
            "grade": grade,
            "recommendation": recommendation,
            "reason": reason
        }