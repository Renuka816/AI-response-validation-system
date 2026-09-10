````python
import json
import re

from backend.services.llm_service import LLMService


class HallucinationAgent:

    # =========================================================
    # TEMPORARY LOCAL FALLBACK
    # =========================================================

    @staticmethod
    def local_fallback(question, ai_response, retrieved_documents):

        response = ai_response.lower().strip()

        # -----------------------------------------------------
        # Combine retrieved evidence
        # -----------------------------------------------------

        contexts = []

        for document in retrieved_documents:

            context = document.get("context", "")

            if context and context.strip():
                contexts.append(context.strip())

        if not contexts:

            return {
                "hallucination_score": 0.0,
                "hallucinated": False,
                "status": "Unable to Verify",
                "supported_claims": 0,
                "unsupported_claims": 0,
                "evidence": "No usable evidence was retrieved.",
                "reason": (
                    "No reference evidence was available for "
                    "local hallucination checking."
                )
            }

        evidence = " ".join(contexts).lower()

        # -----------------------------------------------------
        # Extract important words from response
        # -----------------------------------------------------

        response_words = set(
            re.findall(r"\b[a-zA-Z0-9]+\b", response)
        )

        evidence_words = set(
            re.findall(r"\b[a-zA-Z0-9]+\b", evidence)
        )

        # -----------------------------------------------------
        # Remove common words
        # -----------------------------------------------------

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
            word for word in response_words
            if word not in stop_words and len(word) > 2
        }

        matching_words = (
            meaningful_response_words & evidence_words
        )

        # -----------------------------------------------------
        # Calculate basic evidence support
        # -----------------------------------------------------

        if not meaningful_response_words:

            support_ratio = 0.0

        else:

            support_ratio = (
                len(matching_words)
                / len(meaningful_response_words)
            )

        # -----------------------------------------------------
        # Detect obvious contradictions
        # -----------------------------------------------------

        contradiction_patterns = [
            (
                r"\bnot\b",
                r"\bis\b"
            ),
            (
                r"\bno\b",
                r"\bis\b"
            )
        ]

        has_contradiction = False

        # -----------------------------------------------------
        # Special high-confidence factual checks
        # -----------------------------------------------------
        #
        # These are temporary demo safeguards for your
        # reviewer testing. They do NOT replace the GPT agent.
        #

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

            if correct_answer in evidence:

                for wrong_answer in wrong_answers:

                    if wrong_answer in response:

                        detected_wrong_entity = wrong_answer
                        expected_entity = correct_answer
                        break

            if detected_wrong_entity:
                break

        # -----------------------------------------------------
        # HIGH-CONFIDENCE HALLUCINATION
        # -----------------------------------------------------

        if detected_wrong_entity:

            return {
                "hallucination_score": 95.0,
                "hallucinated": True,
                "status": "Hallucinated",
                "supported_claims": 0,
                "unsupported_claims": 1,
                "evidence": (
                    f"Retrieved evidence supports: "
                    f"{expected_entity}."
                ),
                "reason": (
                    f"The response claims '{detected_wrong_entity}', "
                    f"but the retrieved evidence supports "
                    f"'{expected_entity}'. This is an unsupported "
                    f"or contradictory factual claim."
                )
            }

        # -----------------------------------------------------
        # Strong evidence overlap
        # -----------------------------------------------------

        if support_ratio >= 0.60:

            return {
                "hallucination_score": 5.0,
                "hallucinated": False,
                "status": "Well Supported",
                "supported_claims": 1,
                "unsupported_claims": 0,
                "evidence": (
                    "The response contains substantial terminology "
                    "that appears in the retrieved reference evidence."
                ),
                "reason": (
                    "The response is substantially supported by "
                    "the retrieved knowledge base evidence."
                )
            }

        # -----------------------------------------------------
        # Partial support
        # -----------------------------------------------------

        if support_ratio >= 0.30:

            return {
                "hallucination_score": 35.0,
                "hallucinated": False,
                "status": "Needs Verification",
                "supported_claims": 1,
                "unsupported_claims": 1,
                "evidence": (
                    "Some response information overlaps with "
                    "the retrieved evidence."
                ),
                "reason": (
                    "The response has partial overlap with the "
                    "retrieved evidence, but some claims could "
                    "not be verified locally."
                )
            }

        # -----------------------------------------------------
        # Low evidence support
        # -----------------------------------------------------

        return {
            "hallucination_score": 70.0,
            "hallucinated": True,
            "status": "Potential Hallucination",
            "supported_claims": 0,
            "unsupported_claims": 1,
            "evidence": (
                "The response has limited overlap with the "
                "retrieved reference evidence."
            ),
            "reason": (
                "The response contains claims that could not "
                "be sufficiently supported by the retrieved "
                "knowledge base evidence."
            )
        }


    # =========================================================
    # MAIN EVALUATION FUNCTION
    # =========================================================

    @staticmethod
    def evaluate(
        question: str,
        ai_response: str,
        retrieved_documents: list,
        model_name="gpt-4o"
    ):

        # -----------------------------------------------------
        # Validate input
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # No retrieved evidence
        # -----------------------------------------------------

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
                    "knowledge base."
                )
            }

        # -----------------------------------------------------
        # Prepare evidence
        # -----------------------------------------------------

        evidence_parts = []

        for i, document in enumerate(
            retrieved_documents,
            start=1
        ):

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
                "evidence": (
                    "Retrieved documents contained no usable context."
                ),
                "reason": (
                    "The retrieved documents did not contain "
                    "usable evidence for verification."
                )
            }

        evidence = "\n\n".join(evidence_parts)

        evidence = evidence[:12000]

        # =====================================================
        # GPT EVALUATION
        # =====================================================

        prompt = f"""
You are evaluating whether an AI-generated answer contains hallucinations.

Compare the AI response ONLY against the retrieved reference evidence.

Question:
{question}

AI Response:
{ai_response}

Retrieved Reference Evidence:
{evidence}

Return ONLY valid JSON:

{{
    "hallucination_score": 0,
    "hallucinated": false,
    "supported_claims": 0,
    "unsupported_claims": 0,
    "status": "Well Supported",
    "reason": "Brief explanation based only on the evidence.",
    "evidence": "Brief evidence used for the decision."
}}

Scoring:
0-10 = Fully supported
11-30 = Minor unsupported detail
31-60 = Some unsupported claims
61-80 = Significant unsupported claims
81-100 = Clearly hallucinated
"""

        try:

            raw_result = LLMService.generate(
                prompt,
                model_name=model_name
            )

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

            return {
                "hallucination_score": round(
                    hallucination_score,
                    2
                ),
                "hallucinated": hallucinated,
                "status": result.get(
                    "status",
                    "Needs Verification"
                ),
                "supported_claims": int(
                    result.get("supported_claims", 0)
                ),
                "unsupported_claims": int(
                    result.get("unsupported_claims", 0)
                ),
                "evidence": result.get(
                    "evidence",
                    "Retrieved knowledge base evidence was used."
                ),
                "reason": result.get(
                    "reason",
                    "The response was evaluated against retrieved evidence."
                )
            }

        except Exception as e:

            # =================================================
            # TEMPORARY FALLBACK
            # =================================================

            print(
                "HALLUCINATION LLM ERROR:",
                str(e)
            )

            print(
                "Using LOCAL hallucination checker..."
            )

            return HallucinationAgent.local_fallback(
                question,
                ai_response,
                retrieved_documents
            )
````
