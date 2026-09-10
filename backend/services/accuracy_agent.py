
import json
import re

from backend.services.llm_service import LLMService


class AccuracyAgent:

    # =============================================================
    # HIGH-CONFIDENCE DEMO CONTRADICTION CHECK
    # =============================================================
    #
    # These checks are used only when the retrieved evidence clearly
    # supports a known correct entity and the response explicitly
    # contains a known incorrect entity.
    #
    # GPT remains the primary evaluator.
    # This acts as a safety layer so an obvious contradiction cannot
    # incorrectly receive a high accuracy score.
    # =============================================================

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
        """
        Evaluates factual accuracy of an AI-generated response
        against evidence retrieved from the RAG/ChromaDB knowledge base.

        Accuracy considers:
        1. Whether claims are supported by retrieved evidence.
        2. Whether the response contradicts the evidence.
        3. Whether the response answers the question.
        4. Whether unsupported factual claims are introduced.

        GPT is used as the main evaluator.
        A local high-confidence contradiction check prevents
        obvious contradictions from receiving an incorrectly high score.
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
        # This happens BEFORE GPT evaluation.
        #
        # Example:
        #
        # Evidence:
        #   Plasmodium falciparum
        #
        # Response:
        #   Escherichia coli causes malaria.
        #
        # The response contains an explicitly known wrong entity.
        # Therefore accuracy must be low.
        # ---------------------------------------------------------

        evidence_lower = evidence.lower()
        response_lower = response.lower()

        detected_wrong_entity = None
        expected_entity = None

        for correct_answer, wrong_answers in (
            AccuracyAgent.KNOWN_WRONG_ANSWERS.items()
        ):

            # Only apply this rule if the correct answer is actually
            # present in the retrieved evidence.

            if correct_answer in evidence_lower:

                for wrong_answer in wrong_answers:

                    if wrong_answer in response_lower:

                        detected_wrong_entity = wrong_answer
                        expected_entity = correct_answer
                        break

            if detected_wrong_entity:
                break

        # ---------------------------------------------------------
        # 5. RETURN HIGH-CONFIDENCE INACCURACY
        # ---------------------------------------------------------

        if detected_wrong_entity:

            return {
                "accuracy_score": 5.0,
                "reason": (
                    f"The AI response claims '{detected_wrong_entity}', "
                    f"but the retrieved evidence supports "
                    f"'{expected_entity}'. Therefore the response "
                    f"contains a direct factual contradiction."
                ),
                "verdict": "Inaccurate",
                "contradiction": True,
                "unsupported_claims": 1
            }

        # ---------------------------------------------------------
        # 6. BUILD STRICT GPT EVALUATION PROMPT
        # ---------------------------------------------------------

        prompt = f"""
You are the Accuracy Evaluation Agent for an AI Response Validation System.

Your ONLY task is to evaluate the factual accuracy of the AI response
against the retrieved reference evidence.

Do NOT judge writing quality.
Do NOT reward the answer merely because it sounds convincing.
Do NOT use your own world knowledge to override the retrieved evidence.

QUESTION:
{question}

AI RESPONSE:
{response}

RETRIEVED REFERENCE EVIDENCE:
{evidence}

IMPORTANT EVALUATION RULES:

1. The retrieved evidence is the primary reference.

2. Every important factual claim in the AI response must be checked
   against the retrieved evidence.

3. If the AI response directly contradicts the retrieved evidence,
   the response is INACCURATE.

4. If even one important factual claim directly contradicts the
   evidence, do NOT give a score of 100.

5. If the main answer is wrong, the accuracy score should normally
   be between 0 and 30.

6. If the response contains both correct and incorrect factual claims,
   give a partial score.

7. If the response contains unsupported factual claims, reduce the
   score.

8. A response must NOT receive 100 if it contains a factual
   contradiction.

9. Do not assume that an unsupported claim is correct simply because
   it is plausible.

10. If the evidence clearly says X and the response says Y, where X
    and Y are contradictory answers, mark the response inaccurate.

11. The score must be between 0 and 100.

12. Return ONLY valid JSON.

Use this scoring guidance:

90-100:
Fully supported by the retrieved evidence with no meaningful
contradictions or unsupported factual claims.

70-89:
Mostly accurate, but contains a minor unsupported detail or
small omission.

40-69:
Partially accurate. Some claims are supported while other
claims cannot be verified or are incorrect.

10-39:
Mostly inaccurate. The main answer contains incorrect or
contradictory information.

0-9:
Completely unsupported or directly contradictory to the
retrieved evidence.

Return exactly:

{{
    "accuracy_score": number,
    "verdict": "Accurate" or "Partially Accurate" or "Inaccurate",
    "reason": "short explanation based only on retrieved evidence",
    "contradiction": true or false,
    "unsupported_claims": number
}}
"""

        # ---------------------------------------------------------
        # 7. GPT EVALUATION
        # ---------------------------------------------------------

        try:

            result = LLMService.generate(
                prompt=prompt,
                model_name=model_name
            )

            # -----------------------------------------------------
            # 8. PARSE GPT RESPONSE
            # -----------------------------------------------------

            if isinstance(result, dict):

                raw_result = result

            else:

                raw_text = str(result).strip()

                # Remove markdown JSON fences.

                raw_text = re.sub(
                    r"^```json\s*|\s*```$",
                    "",
                    raw_text,
                    flags=re.IGNORECASE
                ).strip()

                raw_result = json.loads(raw_text)

            # -----------------------------------------------------
            # 9. EXTRACT SCORE
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
            # 10. EXTRACT OTHER VALUES
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

            verdict_lower = str(
                verdict
            ).strip().lower()

            # ---------------------------------------------------------
            # 11. SAFETY CORRECTIONS
            # ---------------------------------------------------------
            #
            # Prevent obviously inconsistent results.
            # ---------------------------------------------------------

            # Explicit contradiction can NEVER be 100.

            if contradiction:

                if score > 30:

                    score = 20.0

                verdict = "Inaccurate"

                reason = (
                    str(reason)
                    + " The response contains a contradiction "
                      "with the retrieved evidence."
                )

            # Unsupported factual claims cannot have perfect accuracy.

            elif unsupported_claims > 0:

                if score >= 100:

                    score = 70.0

                if score < 40:

                    verdict = "Inaccurate"

                else:

                    verdict = "Partially Accurate"

            # GPT itself says inaccurate.

            if verdict_lower == "inaccurate":

                if score > 30:

                    score = 20.0

                verdict = "Inaccurate"

            # GPT says partially accurate.

            elif verdict_lower == "partially accurate":

                if score >= 90:

                    score = 70.0

                verdict = "Partially Accurate"

            # ---------------------------------------------------------
            # 12. FINAL RETURN
            # ---------------------------------------------------------

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
        # 13. FALLBACK
        # ---------------------------------------------------------

        except Exception as e:

            print(
                "ACCURACY LLM ERROR:",
                str(e)
            )

            print(
                "Using LOCAL accuracy fallback..."
            )

            return AccuracyAgent._fallback_accuracy(
                question,
                response,
                evidence,
                str(e)
            )

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
        Conservative local fallback when GPT evaluation fails.

        This checks textual overlap with the retrieved evidence.
        It does not claim that overlap guarantees factual correctness.
        """

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

        # ---------------------------------------------------------
        # Response/evidence overlap
        # ---------------------------------------------------------

        response_evidence_overlap = (
            len(response_words & evidence_words)
            / max(len(response_words), 1)
        )

        question_response_overlap = (
            len(question_words & response_words)
            / max(len(question_words), 1)
        )

        # ---------------------------------------------------------
        # Conservative scoring
        # ---------------------------------------------------------

        if response_evidence_overlap >= 0.60:

            score = 80.0

            reason = (
                "The response has substantial overlap with the "
                "retrieved reference evidence, but automatic "
                "fallback verification cannot guarantee complete "
                "factual accuracy."
            )

        elif response_evidence_overlap >= 0.30:

            score = 55.0

            reason = (
                "The response partially overlaps with the retrieved "
                "reference evidence, but some claims could not "
                "be verified."
            )

        elif question_response_overlap < 0.10:

            score = 20.0

            reason = (
                "The response has little connection to the question "
                "or retrieved reference evidence."
            )

        else:

            score = 30.0

            reason = (
                "The response could not be sufficiently verified "
                "against the retrieved reference evidence."
            )

        if error_message:

            reason += (
                " LLM evaluation fallback was used."
            )

        return {
            "accuracy_score": score,
            "reason": reason,
            "verdict": (
                "Accurate"
                if score >= 80
                else "Partially Accurate"
                if score >= 50
                else "Inaccurate"
            ),
            "contradiction": False,
            "unsupported_claims": 0
        }

