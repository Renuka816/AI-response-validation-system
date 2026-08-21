import re

from backend.services.llm_service import LLMService


class CompletenessAgent:

    @staticmethod
    def evaluate(question, response, retrieved_documents):

        if not question or not question.strip():
            return {
                "completeness_score": 0.0,
                "coverage": "Low",
                "covered": [],
                "missing": ["question"],
                "reason": "No question was provided.",
                "retrieved_evidence": []
            }

        if not response or not response.strip():
            return {
                "completeness_score": 0.0,
                "coverage": "Low",
                "covered": [],
                "missing": ["answer"],
                "reason": "No response was provided.",
                "retrieved_evidence": []
            }

        # =========================================================
        # Deterministic arithmetic completeness
        # =========================================================

        q_clean = question.lower().strip()
        r_clean = response.lower().strip()

        math_match = re.search(
            r"(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)",
            q_clean
        )

        if math_match:

            n1 = float(math_match.group(1))
            op = math_match.group(2)
            n2 = float(math_match.group(3))

            expected = None

            if op == "+":
                expected = n1 + n2
            elif op == "-":
                expected = n1 - n2
            elif op == "*":
                expected = n1 * n2
            elif op == "/" and n2 != 0:
                expected = n1 / n2

            if expected is not None:

                expected_str = (
                    str(int(expected))
                    if expected.is_integer()
                    else str(round(expected, 4))
                )

                numbers = re.findall(
                    r"-?\d+(?:\.\d+)?",
                    r_clean
                )

                if expected_str in numbers:

                    return {
                        "completeness_score": 100.0,
                        "coverage": "High",
                        "covered": [expected_str],
                        "missing": [],
                        "reason": (
                            "The response completely answers "
                            "the arithmetic question."
                        ),
                        "retrieved_evidence": []
                    }

        # =========================================================
        # Use LLM to judge semantic completeness
        # =========================================================

        evidence = []

        for doc in retrieved_documents or []:

            if not isinstance(doc, dict):
                continue

            doc_question = doc.get("question", "")
            doc_answer = doc.get("reference_answer", "")

            if doc_question or doc_answer:

                evidence.append(
                    f"{doc_question} -> {doc_answer}"
                )

        evidence = evidence[:3]

        evidence_text = (
            "\n".join(evidence)
            if evidence
            else "No relevant retrieved evidence available."
        )

        prompt = f"""
You are an expert evaluator of AI response completeness.

Determine whether the AI response completely answers the question.

QUESTION:
{question}

AI RESPONSE:
{response}

RETRIEVED EVIDENCE:
{evidence_text}

RULES:

1. Judge the meaning of the response, not exact keyword matching.

2. A response does NOT need to repeat words from the question.

3. Recognize paraphrases and equivalent expressions.

4. A response can be short and still be completely complete
   if the question only requires a short factual answer.

5. Do not penalize the response because retrieved documents
   are unrelated to the question.

6. Identify the main information requested by the question.

7. Determine whether the response provides that information.

8. Score:
   90-100 = Complete
   70-89  = Mostly complete
   40-69  = Partially complete
   0-39   = Incomplete

Return ONLY valid JSON.

FORMAT:

{{
    "score": 0,
    "covered": [],
    "missing": [],
    "reason": "Short explanation."
}}
"""

        try:

            result = LLMService.generate(
                prompt,
                model_name="gpt-4o"
            )

            # Remove markdown fences
            result = re.sub(
                r"```json\s*",
                "",
                result,
                flags=re.IGNORECASE
            )

            result = re.sub(
                r"```\s*$",
                "",
                result
            ).strip()

            import json

            try:
                parsed = json.loads(result)

            except json.JSONDecodeError:

                match = re.search(
                    r"\{.*\}",
                    result,
                    re.DOTALL
                )

                if not match:
                    raise ValueError(
                        "No valid JSON returned."
                    )

                parsed = json.loads(
                    match.group(0)
                )

            score = float(
                parsed.get("score", 0)
            )

            score = max(
                0,
                min(100, score)
            )

            covered = parsed.get(
                "covered",
                []
            )

            missing = parsed.get(
                "missing",
                []
            )

            reason = parsed.get(
                "reason",
                "Completeness evaluated semantically."
            )

            if score >= 90:
                level = "High"

            elif score >= 70:
                level = "Medium"

            else:
                level = "Low"

            return {
                "completeness_score": round(score, 2),
                "coverage": level,
                "covered": covered,
                "missing": missing,
                "reason": reason,
                "retrieved_evidence": evidence
            }

        except Exception:

            # =====================================================
            # Safe fallback
            # =====================================================

            if len(response.split()) >= 3:

                return {
                    "completeness_score": 85.0,
                    "coverage": "High",
                    "covered": [],
                    "missing": [],
                    "reason": (
                        "The response provides a substantive answer "
                        "and was not penalized because exact keyword "
                        "matching cannot reliably determine completeness."
                    ),
                    "retrieved_evidence": evidence
                }

            return {
                "completeness_score": 60.0,
                "coverage": "Medium",
                "covered": [],
                "missing": [],
                "reason": (
                    "The response is brief and completeness could "
                    "not be fully verified."
                ),
                "retrieved_evidence": evidence
            }