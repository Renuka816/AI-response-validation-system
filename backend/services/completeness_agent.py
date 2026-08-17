import re


class CompletenessAgent:

    @staticmethod
    def evaluate(question, response, retrieved_documents):

        q_clean = question.lower().strip()
        r_clean = response.lower().strip()

        # Math / Arithmetic completeness check
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
                        "completeness_score": 100.0,
                        "coverage": "High",
                        "covered": [exp_str],
                        "missing": [],
                        "reason": "The response completely answers the arithmetic prompt.",
                        "retrieved_evidence": []
                    }

        stop_words = {
            "what", "is", "the", "a", "an", "of", "to", "in", "for", "on", "are", 
            "with", "who", "how", "why", "which", "where", "does", "do", "did", "and", "or"
        }

        question_words = set(re.findall(r"\w+", q_clean))
        response_words = set(re.findall(r"\w+", r_clean))

        substantive_words = [w for w in question_words if w not in stop_words or w.isdigit()]

        covered = []
        missing = []

        for word in substantive_words:
            if word in response_words:
                covered.append(word)
            else:
                missing.append(word)

        if not substantive_words:
            completeness_score = 100.0 if len(response.strip()) > 0 else 0.0
        else:
            coverage = len(covered) / max(len(substantive_words), 1)
            completeness_score = round(coverage * 100, 2)
            # Boost score for concise complete answers to short questions
            if len(question_words) <= 6 and len(response.strip()) > 0 and completeness_score > 0:
                completeness_score = max(completeness_score, 85.0)

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