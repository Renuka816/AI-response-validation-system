from backend.services.rag_service import retrieve_documents

from backend.services.accuracy_agent import AccuracyAgent
from backend.services.hallucination_agent import HallucinationAgent
from backend.services.completeness_agent import CompletenessAgent
from backend.services.relevance_agent import RelevanceJudgeAgent

from backend.services.scoring_service import ScoringService

from backend.utils.helper import get_current_timestamp
from backend.utils.logger import logger


class EvaluationService:

    # =========================================================
    # MAIN EVALUATION
    # =========================================================

    @staticmethod
    def process_request(request):

        logger.info("Evaluation Started")

        # =====================================================
        # 1. RAG RETRIEVAL
        # =====================================================

        retrieved_docs = retrieve_documents(
            request.question
        )

        # =====================================================
        # 2. ACCURACY EVALUATION
        # =====================================================
        #
        # The LLM receives:
        #
        # QUESTION
        # AI RESPONSE
        # RETRIEVED EVIDENCE
        #
        # No hard-coded question/reference mapping is used.
        #

        accuracy_result = AccuracyAgent.evaluate(
            question=request.question,
            response=request.response,
            documents=retrieved_docs,
            model_name="gpt-4o"
        )

        # =====================================================
        # 3. HALLUCINATION EVALUATION
        # =====================================================

        hallucination_result = HallucinationAgent.evaluate(
            request.response,
            retrieved_docs
        )

        # =====================================================
        # 4. RELEVANCE EVALUATION
        # =====================================================

        relevance_result = RelevanceJudgeAgent.evaluate(
            question=request.question,
            response=request.response,
            retrieved_docs=retrieved_docs
        )

        # =====================================================
        # 5. COMPLETENESS EVALUATION
        # =====================================================

        completeness_result = CompletenessAgent.evaluate(
            request.question,
            request.response,
            retrieved_docs
        )

        # =====================================================
        # 6. FINAL SCORE
        # =====================================================

        final_result = ScoringService.calculate_final_score(
            accuracy_result["accuracy_score"],
            hallucination_result["hallucination_score"],
            relevance_result["relevance_score"],
            completeness_result["completeness_score"]
        )

        logger.info("Evaluation Completed")

        # =====================================================
        # 7. RETURN COMPLETE EVALUATION
        # =====================================================

        return {

            "question": request.question,

            "response": request.response,

            "timestamp": get_current_timestamp(),

            # RAG evidence
            "retrieved_documents": retrieved_docs,

            # Individual agents
            "accuracy": accuracy_result,

            "hallucination": hallucination_result,

            "relevance": relevance_result,

            "completeness": completeness_result,

            # Final verdict
            "final_result": final_result
        }