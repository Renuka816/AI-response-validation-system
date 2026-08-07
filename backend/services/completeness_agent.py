import re


class CompletenessAgent:

    @staticmethod
    def evaluate(question, response, retrieved_documents):

        question_words = set(
            re.findall(r"\w+", question.lower())
        )

        response_words = set(
            re.findall(r"\w+", response.lower())
        )

        covered = []
        missing = []

        for word in question_words:

            if len(word) < 4:
                continue

            if word in response_words:
                covered.append(word)
            else:
                missing.append(word)

        coverage = len(covered) / max(len(question_words), 1)

        completeness_score = round(coverage * 100, 2)

        if completeness_score >= 80:
            level = "High"
        elif completeness_score >= 50:
            level = "Medium"
        else:
            level = "Low"

        # -------------------------------
        # Evidence from retrieved docs
        # -------------------------------

        evidence = []

        for doc in retrieved_documents:

            question = doc.get("question", "")

            answer = doc.get("reference_answer", "")

            evidence.append(f"{question} → {answer}")

        evidence = evidence[:3]

        reason = (
            f"The response covers {len(covered)} important aspects "
            f"and misses {len(missing)} important aspects."
        )

        return {

            "completeness_score": completeness_score,

            "coverage": level,

            "covered": covered,

            "missing": missing,

            "reason": reason,

            "retrieved_evidence": evidence

        }