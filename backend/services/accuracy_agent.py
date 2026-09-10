
import json
import re

from backend.services.llm_service import LLMService


class AccuracyAgent:

    # =============================================================
    # HIGH-CONFIDENCE DEMO CONTRADICTIONS
    # =============================================================
    #
    # These are aligned with the factual checks used by the
    # HallucinationAgent.
    #
    # They are NOT the main accuracy mechanism.
    # GPT + RAG evidence remain the primary evaluation mechanism.
    #
    # These checks make sure that an explicitly known contradiction
    # cannot accidentally receive a high accuracy score.
    #

    KNOWN_WRONG_ANSWERS = {

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

    # =============================================================
    # MAIN EVALUATION
    # =============================================================

    @staticmethod
    def evaluate(
        question,
        response,
        documents=None,
        model_name="gpt-4o"
    ):

        # ---------------------------------------------------------
        # 1. INPUT VALIDATION
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 2. PREPARE RETRIEVED EVIDENCE
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 3. NO EVIDENCE
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 4. HIGH-CONFIDENCE LOCAL CONTRADICTION CHECK
        # ---------------------------------------------------------
        #
        # IMPORTANT:
        #
        # This happens BEFORE asking GPT.
        #
        # Example:
        #
        # Evidence:
        # Plasmodium falciparum
        #
        # Response:
        # Escherichia coli causes malaria.
        #
        # The response contains a known incorrect entity while
        # the evidence contains the expected entity.
        #
        # Therefore accuracy MUST NOT be allowed to remain high.
        #

        local_contradiction = AccuracyAgent._detect_known_contradiction(
            response,
            evidence
        )

        if local_contradiction:

            expected_answer = local_contradiction["expected"]
            wrong_answer = local_contradiction["wrong"]

            return {
                "accuracy_score": 10.0,
                "reason": (
                    f"The response contains the incorrect factual claim "
                    f"'{wrong_answer}', while the retrieved evidence "
                    f"supports '{expected_answer}'. Therefore the response "
                    f"is factually inaccurate."
                ),
                "verdict": "Inaccurate",
                "contradiction": True,
                "unsupported_claims": 1
            }

        # ---------------------------------------------------------
        # 5. BUILD GPT ACCURACY PROMPT
        # ---------------------------------------------------------

        prompt = f"""
You are an Accuracy Evaluation Agent for an AI Response Validation System.

Your task is to evaluate ONLY the factual accuracy of the AI-generated
response against the retrieved reference evidence.

IMPORTANT RULES:

1. Treat the retrieved evidence as the primary reference.
2. Do NOT give a high score merely because the response sounds plausible.
3. Compare the factual claims in the response with the evidence.
4. If the response contradicts the evidence, mark it inaccurate.
5. If the response introduces unsupported factual claims, reduce the score.
6. If some claims are correct and some are incorrect, give a partial score.
7. If the main answer is factually wrong, the score should be low.
8. Do NOT use your own world knowledge to override the retrieved evidence.
9. An explicit factual contradiction must NEVER receive a score of 100.
10. If the response gives the opposite or a clearly different factual
    answer from the evidence, classify it as Inaccurate.
11. The score must be between 0 and 100.
12. Return ONLY valid JSON.

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
"""

        # ---------------------------------------------------------
        # 6. GPT EVALUATION
        # ---------------------------------------------------------

        try:

            result = LLMService.generate(
                prompt=prompt,
                model_name=model_name
            )

            # -----------------------------------------------------
            # 7. PARSE RESULT
            # -----------------------------------------------------

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

            # -----------------------------------------------------
            # 8. EXTRACT SCORE
            # -----------------------------------------------------

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

            # -----------------------------------------------------
            # 9. EXTRACT OTHER FIELDS
            # -----------------------------------------------------

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

            reason = raw_result.get(
                "reason",
                "Accuracy evaluation completed."
            )

            verdict = raw_result.get(
                "verdict",
                "Accurate"
            )

            # -----------------------------------------------------
            # 10. NORMALIZE VERDICT
            # -----------------------------------------------------

            verdict_lower = str(
                verdict
            ).strip().lower()

            # -----------------------------------------------------
            # 11. SAFETY CORRECTIONS
            # -----------------------------------------------------
            #
            # These prevent GPT from producing logically inconsistent
            # results such as:
            #
            # contradiction = true
            # accuracy = 100
            #
            # or:
            #
            # verdict = inaccurate
            # accuracy = 100
            #

            if contradiction:

                score = min(
                    score,
                    25.0
                )

                verdict = "Inaccurate"

                if "contradiction" not in str(reason).lower():

                    reason = (
                        str(reason)
                        + " The response contradicts the retrieved evidence."
                    )

            # -----------------------------------------------------
            # UNSUPPORTED CLAIM CORRECTION
            # -----------------------------------------------------

            if unsupported_claims >= 2:

                score = min(
                    score,
                    45.0
                )

                if verdict_lower == "accurate":

                    verdict = "Partially Accurate"

            elif unsupported_claims == 1:

                score = min(
                    score,
                    70.0
                )

                if verdict_lower == "accurate" and score < 80:

                    verdict = "Partially Accurate"

            # -----------------------------------------------------
            # VERDICT-BASED CORRECTION
            # -----------------------------------------------------

            if verdict_lower == "inaccurate":

                score = min(
                    score,
                    30.0
                )

                verdict = "Inaccurate"

            elif verdict_lower == "partially accurate":

                score = min(
                    score,
                    75.0
                )

                verdict = "Partially Accurate"

            else:

                verdict = "Accurate"

            # -----------------------------------------------------
            # 12. SECOND LOCAL CONTRADICTION CHECK
            # -----------------------------------------------------
            #
            # This is done AFTER GPT as well.
            #
            # It protects against a GPT response such as:
            #
            # accuracy_score = 83
            # contradiction = false
            #
            # when the response actually contains a known wrong entity.
            #

            post_check = AccuracyAgent._detect_known_contradiction(
                response,
                evidence
            )

            if post_check:

                expected_answer = post_check["expected"]
                wrong_answer = post_check["wrong"]

                score = min(
                    score,
                    10.0
                )

                verdict = "Inaccurate"
                contradiction = True
                unsupported_claims = max(
                    unsupported_claims,
                    1
                )

                reason = (
                    f"The response contains the incorrect factual claim "
                    f"'{wrong_answer}', while the retrieved evidence "
                    f"supports '{expected_answer}'. Therefore the response "
                    f"is factually inaccurate."
                )

            # -----------------------------------------------------
            # 13. FINAL RETURN
            # -----------------------------------------------------

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

        # ---------------------------------------------------------
        # 14. ERROR HANDLING
        # ---------------------------------------------------------

        except Exception as e:

            return AccuracyAgent._fallback_accuracy(
                question,
                response,
                evidence,
                str(e)
            )

    # =============================================================
    # KNOWN CONTRADICTION DETECTOR
    # =============================================================

    @staticmethod
    def _detect_known_contradiction(
        response,
        evidence
    ):
        """
        Detects high-confidence factual contradictions.

        Returns:
            {
                "expected": correct entity,
                "wrong": incorrect entity
            }

        or None.
        """

        response_lower = response.lower()
        evidence_lower = evidence.lower()

        for correct_answer, wrong_answers in (
            AccuracyAgent.KNOWN_WRONG_ANSWERS.items()
        ):

            # The expected answer must actually appear in
            # retrieved evidence.

            if correct_answer not in evidence_lower:

                continue

            for wrong_answer in wrong_answers:

                if wrong_answer in response_lower:

                    return {
                        "expected": correct_answer,
                        "wrong": wrong_answer
                    }

        return None

    # =============================================================
    # FALLBACK ACCURACY CHECK
    # =============================================================

    @staticmethod
    def _fallback_accuracy(
        question,
        response,
        evidence,
        error_message=None
    ):
        """
        Conservative local accuracy evaluation used when GPT
        evaluation fails.

        Word overlap alone is NOT treated as proof of accuracy.
        """

        # ---------------------------------------------------------
        # First check for known contradiction.
        # ---------------------------------------------------------

        contradiction = AccuracyAgent._detect_known_contradiction(
            response,
            evidence
        )

        if contradiction:

            return {
                "accuracy_score": 10.0,
                "reason": (
                    f"The response contains the incorrect claim "
                    f"'{contradiction['wrong']}', while the retrieved "
                    f"evidence supports '{contradiction['expected']}'."
                    + (
                        " LLM evaluation fallback was used."
                        if error_message
                        else ""
                    )
                ),
                "verdict": "Inaccurate",
                "contradiction": True,
                "unsupported_claims": 1
            }

        # ---------------------------------------------------------
        # Token extraction
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # No evidence
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Remove common words
        # ---------------------------------------------------------

        stop_words = {
            "the", "is", "are", "was", "were",
            "a", "an", "and", "or", "of", "to",
            "in", "on", "for", "with", "by",
            "from", "as", "that", "this", "it",
            "its", "be", "has", "have", "had",
            "does", "do", "did", "what", "which",
            "who", "how", "when", "where", "why",
            "can", "could", "may", "might",
            "will", "would"
        }

        meaningful_response_words = {
            word
            for word in response_words
            if word not in stop_words
            and len(word) > 2
        }

        meaningful_evidence_words = {
            word
            for word in evidence_words
            if word not in stop_words
            and len(word) > 2
        }

        # ---------------------------------------------------------
        # Evidence overlap
        # ---------------------------------------------------------

        if not meaningful_response_words:

            response_evidence_overlap = 0.0

        else:

            response_evidence_overlap = (
                len(
                    meaningful_response_words
                    & meaningful_evidence_words
                )
                / len(meaningful_response_words)
            )

        # ---------------------------------------------------------
        # Question-response relationship
        # ---------------------------------------------------------

        if not question_words:

            question_response_overlap = 0.0

        else:

            question_response_overlap = (
                len(
                    question_words
                    & response_words
                )
                / len(question_words)
            )

        # ---------------------------------------------------------
        # Conservative fallback scoring
        # ---------------------------------------------------------

        if response_evidence_overlap >= 0.70:

            score = 80.0

            reason = (
                "The response has substantial overlap with the "
                "retrieved reference evidence. However, the local "
                "fallback cannot guarantee complete factual accuracy."
            )

            verdict = "Accurate"

        elif response_evidence_overlap >= 0.40:

            score = 60.0

            reason = (
                "The response partially overlaps with the retrieved "
                "reference evidence, but some claims could not be "
                "fully verified."
            )

            verdict = "Partially Accurate"

        elif question_response_overlap < 0.10:

            score = 20.0

            reason = (
                "The response has little connection to the question "
                "or retrieved reference evidence."
            )

            verdict = "Inaccurate"

        else:

            score = 30.0

            reason = (
                "The response could not be sufficiently verified "
                "against the retrieved reference evidence."
            )

            verdict = "Inaccurate"

        if error_message:

            reason += " LLM evaluation fallback was used."

        return {
            "accuracy_score": score,
            "reason": reason,
            "verdict": verdict,
            "contradiction": False,
            "unsupported_claims": 0
        }
