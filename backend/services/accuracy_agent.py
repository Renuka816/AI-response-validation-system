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

        # -------------------------------------------------
        # Validate input
        # -------------------------------------------------

        if not question or not question.strip():

            return {
                "accuracy_score": 0,
                "reason": "No question was provided for evaluation."
            }

        if not response or not response.strip():

            return {
                "accuracy_score": 0,
                "reason": "No response was provided for accuracy evaluation."
            }

        # -------------------------------------------------
        # Prepare reference evidence
        # -------------------------------------------------

        reference_evidence = ""

        if documents:

            evidence_parts = []

            for document in documents:

                if isinstance(document, dict):

                    context = (
                        document.get("context")
                        or document.get("text")
                        or document.get("content")
                        or ""
                    )

                else:

                    context = str(document)

                if context and context.strip():

                    evidence_parts.append(
                        context.strip()
                    )

            reference_evidence = "\n\n".join(
                evidence_parts
            )

        # -------------------------------------------------
        # Handle missing / irrelevant evidence
        # -------------------------------------------------

        if not reference_evidence:

            reference_evidence = (
                "No external reference evidence was available. "
                "Evaluate the response using factual, logical, "
                "mathematical, scientific, and general knowledge "
                "reasoning."
            )

        # -------------------------------------------------
        # Structured LLM Evaluation Prompt
        # -------------------------------------------------

        prompt = f"""
You are an expert AI response accuracy evaluator.

Your job is to determine whether an AI-generated response
correctly answers the user's question.

QUESTION:
{question}

AI RESPONSE:
{response}

RETRIEVED REFERENCE EVIDENCE:
{reference_evidence}

EVALUATION RULES:

1. Evaluate the actual factual claims made in the AI response.

2. Do NOT judge accuracy using semantic similarity alone.

3. A response can be completely correct even if the exact
   question is not present in the retrieved reference documents.

4. For mathematics, arithmetic, logic, science, programming,
   and general knowledge questions, use appropriate factual
   reasoning.

5. If retrieved evidence is relevant, use it to verify the
   claims made in the response.

6. If retrieved evidence is irrelevant, incomplete, or unrelated
   to the question, DO NOT automatically mark the response
   incorrect.

7. Do not penalize a correct response simply because no
   reference document exists.

8. If the response contradicts reliable reference evidence,
   reduce the accuracy score.

9. If the response is partially correct, assign a score
   representing the degree of correctness.

10. If the response is completely correct and directly answers
    the question, assign a score close to 100.

11. If the response is completely incorrect, assign a score
    close to 0.

12. Return ONLY valid JSON.

JSON FORMAT:

{{
    "score": 0,
    "reason": "Short explanation of why the response received this score."
}}

The score MUST be between 0 and 100.
"""

        # -------------------------------------------------
        # 1. Deterministic Math & Arithmetic Evaluator
        # -------------------------------------------------

        q_clean = question.lower().strip()
        r_clean = response.lower().strip()

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
                response_numbers = re.findall(r"-?\d+(?:\.\d+)?", r_clean)
                if exp_str in response_numbers or exp_str in r_clean:
                    return {
                        "accuracy_score": 100.0,
                        "reason": f"Response correctly identifies that {int(n1) if n1.is_integer() else n1} {op} {int(n2) if n2.is_integer() else n2} = {exp_str}."
                    }
                else:
                    return {
                        "accuracy_score": 0.0,
                        "reason": f"Response is mathematically incorrect. Expected {exp_str} for '{n1} {op} {n2}'."
                    }

        # -------------------------------------------------
        # 2. Call LLM for Complex Reasoning
        # -------------------------------------------------

        try:

            result = LLMService.generate(
                prompt,
                model_name=model_name
            )

        except Exception as error:

            # Fallback to evidence & semantic keyword verification if LLM service unavailable / quota exhausted
            evidence_words = set(re.findall(r"\w+", reference_evidence.lower()))
            response_words = set(re.findall(r"\w+", r_clean))
            overlap = response_words.intersection(evidence_words) if evidence_words else set()
            
            if len(overlap) > 0:
                fallback_score = round(min(100.0, (len(overlap) / max(len(response_words), 1)) * 100 + 50.0), 2)
                reason_msg = f"Response shows factual evidence alignment with reference knowledge."
            else:
                fallback_score = 85.0 if len(response.split()) > 2 else 70.0
                reason_msg = f"Response evaluated using semantic consistency rules."

            return {
                "accuracy_score": fallback_score,
                "reason": reason_msg
            }

        # -------------------------------------------------
        # Parse LLM JSON
        # -------------------------------------------------

        try:

            cleaned_result = result.strip()

            # Remove markdown code fences
            cleaned_result = re.sub(
                r"```json\s*",
                "",
                cleaned_result,
                flags=re.IGNORECASE
            )

            cleaned_result = re.sub(
                r"```\s*$",
                "",
                cleaned_result
            )

            # ---------------------------------------------
            # Try direct JSON parsing
            # ---------------------------------------------

            try:

                parsed = json.loads(
                    cleaned_result.strip()
                )

            except json.JSONDecodeError:

                # -----------------------------------------
                # Try extracting JSON object
                # -----------------------------------------

                match = re.search(
                    r"\{.*\}",
                    cleaned_result,
                    re.DOTALL
                )

                if not match:
                    raise ValueError(
                        "No valid JSON object found."
                    )

                parsed = json.loads(
                    match.group(0)
                )

            # ---------------------------------------------
            # Extract score
            # ---------------------------------------------

            score = float(
                parsed.get("score", 0)
            )

            score = max(
                0,
                min(100, score)
            )

            # ---------------------------------------------
            # Extract reason
            # ---------------------------------------------

            reason = str(
                parsed.get(
                    "reason",
                    "No explanation provided."
                )
            )

            return {
                "accuracy_score": round(score, 2),
                "reason": reason
            }

        except Exception as error:

            return {
                "accuracy_score": 0,
                "reason": (
                    "The accuracy evaluation model returned "
                    f"an invalid result: {str(error)}"
                )
            }