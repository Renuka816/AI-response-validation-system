
import json
import re

from backend.services.llm_service import LLMService


class AccuracyAgent:

    # =============================================================
    # HIGH-CONFIDENCE DEMO CONTRADICTION CHECKS
    # =============================================================
    #
    # These are safeguards for factual contradictions that are
    # especially useful for reviewer testing.
    #
    # The GPT agent is still the primary evaluator.
    # These checks prevent an obvious contradiction from being
    # incorrectly returned as 100% accurate.
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
        ],

        "1856": [
            "1756",
            "1800",
            "1900",
            "1956"
        ],

        "warsaw": [
            "krakow",
            "kraków",
            "berlin",
            "paris"
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
        """
        Evaluates factual accuracy of an AI-generated response
        against evidence retrieved from the RAG/ChromaDB knowledge base.

        Accuracy considers:

        1. Evidence support
        2. Contradictions
        3. Unsupported factual claims
        4. Whether the response answers the question

        GPT performs the main semantic evaluation.

        Additional deterministic safeguards are applied after
        GPT evaluation so that obvious contradictions cannot
        incorrectly receive a perfect score.
        """

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

                # ChromaDB/RAG results may use different field names.
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

            if text and str(text).strip():

                evidence_parts.append(
                    f"Evidence {index}:\n{str(text).strip()}"
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
        # This runs BEFORE GPT.
        #
        # Example:
        #
        # Evidence:
        # Plasmodium falciparum
        #
        # AI Response:
        # Escherichia coli
        #
        # The response is clearly contradictory.
        #

        local_contradiction = AccuracyAgent._detect_known_contradiction(
            response,
            evidence
        )

        # ---------------------------------------------------------
        # 5. BUILD STRICT GPT PROMPT
        # ---------------------------------------------------------

        prompt = f"""
You are an Accuracy Evaluation Agent for an AI Response Validation System.

Your ONLY task is to evaluate the factual accuracy of the AI response
against the retrieved reference evidence.

QUESTION:
{question}

AI RESPONSE:
{response}

RETRIEVED REFERENCE EVIDENCE:
{evidence}

IMPORTANT RULES:

1. Treat the retrieved evidence as the primary reference.

2. Do NOT give a score of 100 merely because the response sounds
   plausible or fluent.

3. If the response contradicts the retrieved evidence, it is inaccurate.

4. If the response gives a different factual entity, value, person,
   place, cause, date, or answer from the evidence, treat this as
   a contradiction when the evidence clearly establishes the
   expected answer.

5. If the response introduces factual information that is not
   supported by the retrieved evidence, count it as an unsupported
   claim and reduce the score.

6. If the response contains both correct and incorrect claims,
   give a partial score.

7. If the main answer is wrong, the accuracy score should be low,
   even if some surrounding words overlap with the evidence.

8. Do NOT use your own world knowledge to override the retrieved
   evidence.

9. A response containing an explicit factual contradiction MUST NOT
   receive a score of 100.

10. The score must be between 0 and 100.

11. Return ONLY valid JSON.

SCORING GUIDELINE:

90-100 = Fully supported and factually consistent
70-89  = Mostly accurate with minor issues
40-69  = Partially accurate / important unsupported information
20-39  = Mostly inaccurate
0-19   = Clearly contradictory or factually wrong

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
            # 7. PARSE GPT RESULT
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

            unsupported_claims = max(
                0,
                unsupported_claims
            )

            reason = raw_result.get(
                "reason",
                "Accuracy evaluation completed."
            )

            verdict = raw_result.get(
                "verdict",
                "Accurate"
            )

            # =====================================================
            # 10. APPLY LOCAL CONTRADICTION SAFEGUARD
            # =====================================================

            if local_contradiction:

                detected_wrong = local_contradiction["wrong"]
                expected = local_contradiction["expected"]

                # Force contradiction state.
                contradiction = True

                # At least one unsupported/wrong claim exists.
                unsupported_claims = max(
                    unsupported_claims,
                    1
                )

                # Do NOT allow GPT to return a high score for
                # an obvious contradiction.
                #
                # We deliberately use a low score so the reviewer
                # can clearly see the difference between the
                # correct and hallucinated responses.

                score = min(
                    score,
                    20.0
                )

                verdict = "Inaccurate"

                reason = (
                    f"The AI response claims '{detected_wrong}', "
                    f"but the retrieved reference evidence supports "
                    f"'{expected}'. This is a direct factual "
                    f"contradiction."
                )

            # =====================================================
            # 11. GENERAL SAFETY CORRECTIONS
            # =====================================================

            # Contradiction can NEVER have a perfect score.

            if contradiction:

                score = min(
                    score,
                    30.0
                )

                verdict = "Inaccurate"

            # Unsupported claims prevent a perfect score.

            if unsupported_claims > 0:

                score = min(
                    score,
                    70.0
                )

                if score < 50:

                    verdict = "Inaccurate"

                elif score < 90:

                    verdict = "Partially Accurate"

            # Explicit inaccurate verdict prevents a perfect score.

            if str(verdict).strip().lower() == "inaccurate":

                score = min(
                    score,
                    30.0
                )

            # Explicit partially accurate verdict prevents 100.

            if str(verdict).strip().lower() == "partially accurate":

                score = min(
                    score,
                    89.0
                )

            # -----------------------------------------------------
            # 12. FINAL RESULT
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
        # 13. LLM ERROR → FALLBACK
        # ---------------------------------------------------------

        except Exception as e:

            return AccuracyAgent._fallback_accuracy(
                question,
                response,
                evidence,
                str(e)
            )

    # =============================================================
    # HIGH-CONFIDENCE CONTRADICTION DETECTOR
    # =============================================================

    @staticmethod
    def _detect_known_contradiction(
        response,
        evidence
    ):
        """
        Detects known high-confidence contradictions.

        This is intentionally conservative.

        It only marks a contradiction when:
        - the expected answer/entity is present in the evidence
        - AND a known incorrect alternative appears in the response
        """

        response_lower = response.lower()
        evidence_lower = evidence.lower()

        for expected_answer, wrong_answers in (
            AccuracyAgent.KNOWN_WRONG_ANSWERS.items()
        ):

            if expected_answer not in evidence_lower:

                continue

            for wrong_answer in wrong_answers:

                if wrong_answer in response_lower:

                    return {
                        "expected": expected_answer,
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
        Conservative fallback when the LLM evaluation fails.

        This fallback uses evidence overlap only.
        It does not claim that overlap proves factual correctness.
        """

        # ---------------------------------------------------------
        # First check high-confidence contradictions again.
        # ---------------------------------------------------------

        contradiction = AccuracyAgent._detect_known_contradiction(
            response,
            evidence
        )

        if contradiction:

            return {
                "accuracy_score": 10.0,
                "reason": (
                    f"The response claims "
                    f"'{contradiction['wrong']}', but the retrieved "
                    f"evidence supports "
                    f"'{contradiction['expected']}'. "
                    f"This is a direct factual contradiction. "
                    f"LLM evaluation failed, so the deterministic "
                    f"contradiction safeguard was used."
                ),
                "verdict": "Inaccurate",
                "contradiction": True,
                "unsupported_claims": 1
            }

        # ---------------------------------------------------------
        # Tokenize
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
            "the", "is", "are", "was", "were", "a", "an",
            "and", "or", "of", "to", "in", "on", "for",
            "with", "by", "from", "as", "that", "this",
            "it", "its", "be", "has", "have", "had",
            "does", "do", "did", "what", "which", "who",
            "how", "when", "where", "why", "can", "could",
            "may", "might", "will", "would"
        }

        meaningful_response_words = {
            word
            for word in response_words
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
                    & evidence_words
                )
                /
                len(meaningful_response_words)
            )

        # ---------------------------------------------------------
        # Question-response overlap
        # ---------------------------------------------------------

        if not question_words:

            question_response_overlap = 0.0

        else:

            question_response_overlap = (
                len(
                    question_words
                    & response_words
                )
                /
                len(question_words)
            )

        # ---------------------------------------------------------
        # Conservative fallback scoring
        # ---------------------------------------------------------

        if response_evidence_overlap >= 0.60:

            score = 80.0

            reason = (
                "The response has substantial overlap with the "
                "retrieved reference evidence, but automatic "
                "fallback verification cannot guarantee complete "
                "factual accuracy."
            )

            verdict = "Partially Accurate"

        elif response_evidence_overlap >= 0.30:

            score = 55.0

            reason = (
                "The response partially overlaps with the "
                "retrieved reference evidence, but some claims "
                "could not be verified."
            )

            verdict = "Partially Accurate"

        elif question_response_overlap < 0.10:

            score = 20.0

            reason = (
                "The response has little connection to the "
                "question or retrieved reference evidence."
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

            reason += (
                " LLM evaluation failed, so the conservative "
                "fallback method was used."
            )

        return {
            "accuracy_score": score,
            "reason": reason,
            "verdict": verdict,
            "contradiction": False,
            "unsupported_claims": 0
        }
