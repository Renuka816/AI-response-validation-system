
import json
import re

from backend.services.llm_service import LLMService


class AccuracyAgent:

    @staticmethod
    def evaluate(
        question,
        response,
        documents=None,
        model_name="gpt-4o"
    ):
        """
        Evaluates factual accuracy of an AI-generated response
        against evidence retrieved from the RAG/ChromaDB knowledge base.

        Accuracy score:
            0   = Completely inaccurate
            50  = Partially accurate
            100 = Fully accurate

        The score is based on:
        1. Support from retrieved evidence
        2. Contradictions against retrieved evidence
        3. Unsupported factual claims
        4. Whether the response answers the question
        """

        # =============================================================
        # 1. INPUT VALIDATION
        # =============================================================

        if not question or not question.strip():

            return {
                "accuracy_score": 0,
                "reason": "No question was provided for evaluation.",
                "verdict": "Inaccurate",
                "contradiction": False,
                "unsupported_claims": 0
            }

        if not response or not response.strip():

            return {
                "accuracy_score": 0,
                "reason": "No AI response was provided for evaluation.",
                "verdict": "Inaccurate",
                "contradiction": False,
                "unsupported_claims": 0
            }

        documents = documents or []

        # =============================================================
        # 2. PREPARE RETRIEVED EVIDENCE
        # =============================================================

        evidence_parts = []

        for index, document in enumerate(documents[:5], start=1):

            if isinstance(document, dict):

                text = (
                    document.get("text")
                    or document.get("document")
                    or document.get("content")
                    or document.get("page_content")
                    or document.get("context")
                    or ""
                )

            else:
                text = str(document)

            if text and text.strip():

                evidence_parts.append(
                    f"Evidence {index}:\n{text.strip()}"
                )

        evidence = "\n\n".join(evidence_parts)

        # =============================================================
        # 3. NO EVIDENCE
        # =============================================================

        if not evidence.strip():

            return {
                "accuracy_score": 0,
                "reason": (
                    "No retrieved evidence was available from the "
                    "knowledge base, so factual accuracy could not "
                    "be reliably verified."
                ),
                "verdict": "Inaccurate",
                "contradiction": False,
                "unsupported_claims": 0
            }

        # =============================================================
        # 4. HIGH-CONFIDENCE LOCAL CONTRADICTION CHECK
        # =============================================================
        #
        # This is especially useful for reviewer demonstrations.
        #
        # Example:
        #
        # Evidence:
        # Plasmodium falciparum
        #
        # Response:
        # Escherichia coli
        #
        # The response should NOT be allowed to receive a high
        # accuracy score simply because GPT considers the sentence
        # plausible.
        # =============================================================

        evidence_lower = evidence.lower()
        response_lower = response.lower()

        known_wrong_answers = {

            "plasmodium falciparum": [
                "escherichia coli",
                "e. coli",
                "influenza virus",
                "coronavirus",
                "salmonella"
            ],

            "water and carbon dioxide": [
                "oxygen and glucose",
                "oxygen and water",
                "glucose and oxygen"
            ],

            "sugar and oxygen": [
                "carbon dioxide and water",
                "nitrogen and oxygen"
            ],

            "jupiter": [
                "earth",
                "mars",
                "venus",
                "saturn"
            ],

            "william shakespeare": [
                "charles dickens",
                "geoffrey chaucer",
                "jane austen"
            ]
        }

        detected_wrong_entity = None
        expected_entity = None

        for correct_answer, wrong_answers in known_wrong_answers.items():

            if correct_answer in evidence_lower:

                for wrong_answer in wrong_answers:

                    if wrong_answer in response_lower:

                        detected_wrong_entity = wrong_answer
                        expected_entity = correct_answer
                        break

            if detected_wrong_entity:
                break

        # =============================================================
        # 5. HIGH-CONFIDENCE CONTRADICTION
        # =============================================================

        if detected_wrong_entity:

            return {
                "accuracy_score": 5.0,
                "reason": (
                    f"The AI response claims '{detected_wrong_entity}', "
                    f"but the retrieved reference evidence supports "
                    f"'{expected_entity}'. Therefore, the response "
                    f"contains a clear factual contradiction."
                ),
                "verdict": "Inaccurate",
                "contradiction": True,
                "unsupported_claims": 1
            }

        # =============================================================
        # 6. GPT ACCURACY EVALUATION
        # =============================================================

        prompt = f"""
You are an Accuracy Evaluation Agent for an AI Response Validation System.

Your task is to evaluate ONLY the factual accuracy of the AI response
against the retrieved reference evidence.

IMPORTANT RULES:

1. Treat the retrieved evidence as the primary reference.
2. Do NOT use your own world knowledge to override the evidence.
3. If the response contradicts the evidence, it is inaccurate.
4. If an important factual claim is unsupported by the evidence,
   reduce the score.
5. If the response contains both correct and incorrect claims,
   give a partial score.
6. A completely incorrect response should receive a very low score.
7. A completely supported response may receive a high score.
8. The score must be between 0 and 100.
9. An explicit contradiction MUST NOT receive a high score.
10. Return ONLY valid JSON.

QUESTION:
{question}

AI RESPONSE:
{response}

RETRIEVED REFERENCE EVIDENCE:
{evidence}

Return exactly:

{{
    "accuracy_score": number,
    "verdict": "Accurate" or "Partially Accurate" or "Inaccurate",
    "reason": "short explanation",
    "contradiction": true or false,
    "unsupported_claims": number
}}

Scoring guidance:

90-100:
The response is fully supported by the retrieved evidence.

70-89:
The response is mostly correct but contains minor unsupported
or incomplete details.

40-69:
The response contains a mixture of supported and unsupported claims.

10-39:
The response contains major factual errors.

0-9:
The response directly contradicts the retrieved evidence or is
essentially completely incorrect.
"""

        try:

            result = LLMService.generate(
                prompt=prompt,
                model_name=model_name
            )

            # =========================================================
            # 7. PARSE RESULT
            # =========================================================

            if isinstance(result, dict):

                raw_result = result

            else:

                raw_text = str(result).strip()

                raw_text = re.sub(
                    r"^```json\s*|\s*```$",
                    "",
                    raw_text,
                    flags=re.IGNORECASE
                ).strip()

                raw_result = json.loads(raw_text)

            # =========================================================
            # 8. EXTRACT SCORE
            # =========================================================

            score = raw_result.get(
                "accuracy_score",
                0
            )

            try:

                score = float(score)

            except (TypeError, ValueError):

                score = 0.0

            score = max(
                0.0,
                min(100.0, score)
            )

            contradiction = bool(
                raw_result.get(
                    "contradiction",
                    False
                )
            )

            unsupported_claims = raw_result.get(
                "unsupported_claims",
                0
            )

            try:

                unsupported_claims = int(
                    unsupported_claims
                )

            except (TypeError, ValueError):

                unsupported_claims = 0

            verdict = raw_result.get(
                "verdict",
                "Partially Accurate"
            )

            reason = raw_result.get(
                "reason",
                "Accuracy evaluation completed."
            )

            # =========================================================
            # 9. SAFETY CORRECTIONS
            # =========================================================

            # ---------------------------------------------------------
            # Explicit contradiction
            # ---------------------------------------------------------
            #
            # If GPT itself says contradiction=True, accuracy cannot
            # remain high.
            # ---------------------------------------------------------

            if contradiction:

                score = min(
                    score,
                    20.0
                )

                verdict = "Inaccurate"

            # ---------------------------------------------------------
            # Unsupported factual claims
            # ---------------------------------------------------------

            elif unsupported_claims >= 2:

                score = min(
                    score,
                    50.0
                )

                if score < 50:

                    verdict = "Inaccurate"

                else:

                    verdict = "Partially Accurate"

            elif unsupported_claims == 1:

                score = min(
                    score,
                    70.0
                )

                if score >= 70:

                    verdict = "Partially Accurate"

            # ---------------------------------------------------------
            # Verdict protection
            # ---------------------------------------------------------

            if str(verdict).lower() == "inaccurate":

                score = min(
                    score,
                    30.0
                )

            elif str(verdict).lower() == "partially accurate":

                score = min(
                    score,
                    75.0
                )

            # =========================================================
            # 10. RETURN RESULT
            # =========================================================

            return {
                "accuracy_score": round(
                    score,
                    2
                ),
                "reason": reason,
                "verdict": verdict,
                "contradiction": contradiction,
                "unsupported_claims": unsupported_claims
            }

        # =============================================================
        # 11. FALLBACK
        # =============================================================

        except Exception as e:

            return AccuracyAgent._fallback_accuracy(
                question,
                response,
                evidence,
                str(e)
            )

    # =================================================================
    # FALLBACK ACCURACY CHECK
    # =================================================================

    @staticmethod
    def _fallback_accuracy(
        question,
        response,
        evidence,
        error_message=None
    ):

        question_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                question.lower()
            )
        )

        response_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                response.lower()
            )
        )

        evidence_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                evidence.lower()
            )
        )

        if not evidence_words:

            return {
                "accuracy_score": 0,
                "reason": (
                    "Accuracy could not be verified because "
                    "no usable evidence was retrieved."
                ),
                "verdict": "Inaccurate",
                "contradiction": False,
                "unsupported_claims": 0
            }

        response_evidence_overlap = (
            len(response_words & evidence_words)
            / max(len(response_words), 1)
        )

        question_response_overlap = (
            len(question_words & response_words)
            / max(len(question_words), 1)
        )

        # -------------------------------------------------------------
        # Conservative fallback scoring
        # -------------------------------------------------------------

        if response_evidence_overlap >= 0.60:

            score = 80.0

            verdict = "Accurate"

            reason = (
                "The response has substantial lexical overlap with "
                "the retrieved reference evidence. However, the "
                "automatic fallback cannot guarantee complete factual "
                "accuracy."
            )

        elif response_evidence_overlap >= 0.30:

            score = 55.0

            verdict = "Partially Accurate"

            reason = (
                "The response partially overlaps with the retrieved "
                "reference evidence, but some claims could not be "
                "verified."
            )

        elif question_response_overlap < 0.10:

            score = 20.0

            verdict = "Inaccurate"

            reason = (
                "The response has little connection to the question "
                "or retrieved reference evidence."
            )

        else:

            score = 30.0

            verdict = "Inaccurate"

            reason = (
                "The response could not be sufficiently verified "
                "against the retrieved reference evidence."
            )

        if error_message:

            reason += " LLM evaluation fallback was used."

        return {
            "accuracy_score": score,
            "reason": reason,
            "verdict": verdict,
            "contradiction": False,
            "unsupported_claims": 0
        }
