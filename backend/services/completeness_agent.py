import json
import re

from backend.services.llm_service import LLMService


class CompletenessAgent:

    @staticmethod
    def evaluate(question, response, retrieved_documents):

        # =========================================================
        # 0. Basic validation
        # =========================================================

        if not question or not question.strip():
            return {
                "completeness_score": 0.0,
                "coverage": "Very Low",
                "covered": [],
                "missing": ["question"],
                "reason": "No question was provided.",
                "retrieved_evidence": []
            }

        if not response or not response.strip():
            return {
                "completeness_score": 0.0,
                "coverage": "Very Low",
                "covered": [],
                "missing": ["answer"],
                "reason": "No response was provided.",
                "retrieved_evidence": []
            }

        q_clean = question.lower().strip()
        r_clean = response.lower().strip()

        # =========================================================
        # 1. Prepare retrieved evidence
        # =========================================================

        evidence = []

        for doc in retrieved_documents or []:

            if not isinstance(doc, dict):
                continue

            doc_question = str(
                doc.get("question", "")
            ).strip()

            doc_answer = str(
                doc.get("reference_answer", "")
            ).strip()

            if doc_question or doc_answer:
                evidence.append(
                    f"{doc_question} -> {doc_answer}"
                )

        evidence = evidence[:5]

        # =========================================================
        # 2. Deterministic arithmetic completeness
        # =========================================================

        math_match = re.search(
            r"(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)",
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
                        "retrieved_evidence": evidence
                    }

        # =========================================================
        # 3. Deterministic factual completeness
        #
        # This allows completeness evaluation even when the
        # external LLM APIs have no quota.
        # =========================================================

        def normalize(text):
            return set(
                re.findall(
                    r"\b[a-zA-Z]{3,}\b",
                    text.lower()
                )
            )

        question_words = normalize(q_clean)
        response_words = normalize(r_clean)

        # Remove common question words
        stop_words = {
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
            "does",
            "did",
            "are",
            "was",
            "were",
            "the",
            "is",
            "a",
            "an",
            "of",
            "to",
            "for",
            "in",
            "on",
            "and",
            "or",
            "with",
            "from"
        }

        meaningful_question_words = (
            question_words - stop_words
        )

        matched_words = (
            meaningful_question_words
            & response_words
        )

        # =========================================================
        # Special handling for "What causes..." questions
        # =========================================================

        if (
            q_clean.startswith("what causes")
            or q_clean.startswith("what cause")
            or "cause of" in q_clean
        ):

            causal_patterns = [
                r"\bcaused by\b",
                r"\bcauses\b",
                r"\bcause\b",
                r"\bdue to\b",
                r"\bresult of\b",
                r"\bresults from\b",
                r"\btransmitted by\b",
                r"\bspread by\b"
            ]

            has_causal_answer = any(
                re.search(pattern, r_clean)
                for pattern in causal_patterns
            )

            if has_causal_answer and len(r_clean.split()) >= 3:

                return {
                    "completeness_score": 100.0,
                    "coverage": "High",
                    "covered": [
                        "The cause requested by the question"
                    ],
                    "missing": [],
                    "reason": (
                        "The response directly identifies the cause "
                        "requested by the question."
                    ),
                    "retrieved_evidence": evidence
                }

        # =========================================================
        # Special handling for "Who..." questions
        # =========================================================

        if q_clean.startswith("who "):

            if len(r_clean.split()) >= 1:

                return {
                    "completeness_score": 95.0,
                    "coverage": "High",
                    "covered": [
                        "The person or entity requested by the question"
                    ],
                    "missing": [],
                    "reason": (
                        "The response provides a direct answer "
                        "to the who-question."
                    ),
                    "retrieved_evidence": evidence
                }

        # =========================================================
        # Special handling for "When..." questions
        # =========================================================

        if q_clean.startswith("when "):

            date_or_year = re.search(
                r"\b(1[0-9]{3}|20[0-9]{2}|21[0-9]{2})\b",
                r_clean
            )

            if date_or_year:

                return {
                    "completeness_score": 95.0,
                    "coverage": "High",
                    "covered": [
                        "The date or time requested by the question"
                    ],
                    "missing": [],
                    "reason": (
                        "The response provides a date or time "
                        "answer to the question."
                    ),
                    "retrieved_evidence": evidence
                }

        # =========================================================
        # General semantic keyword coverage
        # =========================================================

        if meaningful_question_words:

            keyword_coverage = (
                len(matched_words)
                / len(meaningful_question_words)
            ) * 100

        else:
            keyword_coverage = 0

        # Strong overlap
        if keyword_coverage >= 70 and len(r_clean.split()) >= 3:

            return {
                "completeness_score": 90.0,
                "coverage": "High",
                "covered": list(matched_words),
                "missing": [],
                "reason": (
                    "The response provides the main information "
                    "requested by the question."
                ),
                "retrieved_evidence": evidence
            }

        # Moderate overlap
        if keyword_coverage >= 40:

            return {
                "completeness_score": 75.0,
                "coverage": "Medium",
                "covered": list(matched_words),
                "missing": [
                    "Some requested information may be missing."
                ],
                "reason": (
                    "The response addresses part of the question "
                    "but may not provide complete coverage."
                ),
                "retrieved_evidence": evidence
            }

        # =========================================================
        # 4. LLM fallback
        #
        # Only reached when deterministic evaluation cannot
        # confidently determine completeness.
        # =========================================================

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

Rules:

1. Judge completeness, not hallucination.
2. Judge meaning rather than exact keyword matching.
3. Recognize paraphrases.
4. A short factual answer can be completely complete.
5. Do not penalize unrelated retrieved evidence.
6. Identify the information requested by the question.
7. Determine whether the response provides that information.

Scoring:

90-100 = Complete
70-89 = Mostly Complete
40-69 = Partially Complete
0-39 = Incomplete

Return ONLY valid JSON.

{{
    "score": 95,
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

            if not result:
                raise ValueError(
                    "LLM returned an empty response."
                )

            result = result.strip()

            result = re.sub(
                r"^```json\s*",
                "",
                result,
                flags=re.IGNORECASE
            )

            result = re.sub(
                r"^```\s*",
                "",
                result
            )

            result = re.sub(
                r"\s*```$",
                "",
                result
            ).strip()

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
                        "LLM returned invalid JSON."
                    )

                parsed = json.loads(
                    match.group(0)
                )

            score = float(
                parsed.get("score", 0)
            )

            score = max(
                0.0,
                min(100.0, score)
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

            if not isinstance(covered, list):
                covered = [str(covered)]

            if not isinstance(missing, list):
                missing = [str(missing)]

            if score >= 90:
                level = "High"
            elif score >= 70:
                level = "Medium"
            elif score >= 40:
                level = "Low"
            else:
                level = "Very Low"

            return {
                "completeness_score": round(score, 2),
                "coverage": level,
                "covered": covered,
                "missing": missing,
                "reason": reason,
                "retrieved_evidence": evidence
            }

        # =========================================================
        # 5. Final safe fallback
        # =========================================================

        except Exception as e:

            print(
                "\n========== COMPLETENESS AGENT ERROR =========="
            )

            print(
                f"Error type: {type(e).__name__}"
            )

            print(
                f"Error message: {e}"
            )

            print(
                "===============================================\n"
            )

            return {
                "completeness_score": 60.0,
                "coverage": "Low",
                "covered": [],
                "missing": [],
                "reason": (
                    "Semantic completeness evaluation was unavailable."
                ),
                "retrieved_evidence": evidence
            }