def generate_relevance_reason(score, keyword_coverage, context_alignment):
    if score >= 85:
        return (
            "The response directly answers the user's question, "
            "covers the main concepts, and aligns well with the retrieved context."
        )

    elif score >= 70:
        return (
            "The response is generally relevant to the question, "
            "but some important concepts or supporting context are missing."
        )

    elif score >= 50:
        return (
            "The response is partially related to the question, "
            "but it does not fully address the requested information."
        )

    else:
        return (
            "The response has low relevance because it does not sufficiently address "
            "the user's question."
        )