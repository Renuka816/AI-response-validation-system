import json
import re

from backend.services.llm_service import LLMService


class HallucinationAgent:

    @staticmethod
    def evaluate(
        question: str,
        ai_response: str,
        retrieved_documents: list,
        model_name="gpt-4o"
    ):

        # =========================================================
        # Validate input
        # =========================================================

        if not ai_response or not ai_response.strip():

            return {
                "hallucination_score": 100.0,
                "hallucinated": True,
                "status": "Invalid Response",
                "supported_claims": 0,
                "unsupported_claims": 1,
                "evidence": "No AI response was provided.",
                "reason": "There is no response available to evaluate."
            }

        # =========================================================
        # No retrieved evidence
        # =========================================================

        if not retrieved_documents:

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "Unable to Verify",
                "supported_claims": 0,
                "unsupported_claims": 0,
                "evidence": "No retrieved evidence was available.",
                "reason": (
                    "No relevant evidence was retrieved from the "
                    "knowledge base, so hallucination could not be "
                    "reliably determined."
                )
            }

        # =========================================================
        # Prepare retrieved evidence
        # =========================================================

        evidence_parts = []

        for i, document in enumerate(retrieved_documents, start=1):

            context = document.get("context", "")

            if context and context.strip():

                evidence_parts.append(
                    f"Evidence {i}:\n{context.strip()}"
                )

        if not evidence_parts:

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "Unable to Verify",
                "supported_claims": 0,
                "unsupported_claims": 0,
                "evidence": "Retrieved documents contained no usable context.",
                "reason": (
                    "The retrieved documents did not contain usable "
                    "evidence for verification."
                )
            }

        evidence = "\n\n".join(evidence_parts)

        # =========================================================
        # Limit evidence size
        # =========================================================

        evidence = evidence[:12000]

        # =========================================================
        # LLM hallucination evaluation
        # =========================================================

        prompt = f"""
You are evaluating whether an AI-generated answer contains hallucinations.

Your task is to compare the AI response ONLY against the retrieved
reference evidence.

Do NOT use your own general knowledge.

A hallucination occurs when the AI response:

1. Makes a factual claim that is contradicted by the evidence.
2. Introduces a factual claim that is not supported by the evidence.
3. Gives an incorrect entity, number, date, name, place, cause, or fact
   when the evidence provides the correct information.

A response can contain multiple claims.

IMPORTANT:
- Do not judge based only on wording similarity.
- Check the actual meaning of the claims.
- If the evidence says one entity is correct and the response replaces
  it with another entity, mark that claim as unsupported or contradicted.
- If the response is fully supported by the evidence, hallucination_score
  should be 0.
- If the response contains clearly false or unsupported claims,
  hallucination_score should be high.
- Do not assume that a response is correct merely because it sounds
  similar to the evidence.

Question:
{question}

AI Response:
{ai_response}

Retrieved Reference Evidence:
{evidence}

Return ONLY valid JSON in exactly this structure:

{{
    "hallucination_score": 0,
    "hallucinated": false,
    "supported_claims": 0,
    "unsupported_claims": 0,
    "status": "Well Supported",
    "reason": "Brief explanation based only on the evidence.",
    "evidence": "Brief evidence used for the decision."
}}

Scoring guidance:

0-10:
Fully or almost fully supported.

11-30:
Minor unsupported detail, but mostly supported.

31-60:
Some unsupported or questionable claims.

61-80:
Significant unsupported or contradictory claims.

81-100:
Clearly hallucinated or substantially contradicted by the evidence.
"""

        try:

            raw_result = LLMService.generate(
                prompt,
                model_name=model_name
            )

            # =====================================================
            # Clean JSON returned by LLM
            # =====================================================

            cleaned_result = raw_result.strip()

            cleaned_result = re.sub(
                r"^```json\s*",
                "",
                cleaned_result,
                flags=re.IGNORECASE
            )

            cleaned_result = re.sub(
                r"^```\s*",
                "",
                cleaned_result
            )

            cleaned_result = re.sub(
                r"\s*```$",
                "",
                cleaned_result
            )

            result = json.loads(cleaned_result)

            # =====================================================
            # Validate values
            # =====================================================

            hallucination_score = float(
                result.get("hallucination_score", 0)
            )

            hallucination_score = max(
                0.0,
                min(100.0, hallucination_score)
            )

            hallucinated = bool(
                result.get(
                    "hallucinated",
                    hallucination_score >= 50
                )
            )

            supported_claims = int(
                result.get("supported_claims", 0)
            )

            unsupported_claims = int(
                result.get("unsupported_claims", 0)
            )

            status = result.get(
                "status",
                "Needs Verification"
            )

            reason = result.get(
                "reason",
                "The response was evaluated against retrieved evidence."
            )

            evidence_result = result.get(
                "evidence",
                "Retrieved knowledge base evidence was used."
            )

            return {
                "hallucination_score": round(
                    hallucination_score,
                    2
                ),
                "hallucinated": hallucinated,
                "status": status,
                "supported_claims": supported_claims,
                "unsupported_claims": unsupported_claims,
                "evidence": evidence_result,
                "reason": reason
            }

        except Exception as e:

            print(
                "HALLUCINATION AGENT ERROR:",
                str(e)
            )

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "Evaluation Error",
                "supported_claims": 0,
                "unsupported_claims": 0,
                "evidence": "LLM evaluation could not be completed.",
                "reason": (
                    f"Hallucination evaluation failed: {str(e)}"
                )
            }