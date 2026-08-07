from backend.services.rag_service import retrieve_documents
from backend.services.knowledge_agent import KnowledgeAgent
from backend.services.hallucination_agent import HallucinationAgent
from backend.services.completeness_agent import CompletenessAgent
from backend.services.scoring_service import ScoringService
from backend.services.relevance_agent import RelevanceJudgeAgent

from backend.utils.helper import get_current_timestamp
from backend.utils.logger import logger

from backend.data.reference_answers import REFERENCE_ANSWERS


class EvaluationService:

    # -----------------------------------------
    # Reference Answer Mapping
    # -----------------------------------------
    @staticmethod
    def get_reference_answer(question):
        q = question.lower()

        if "photosynthesis" in q:
            return REFERENCE_ANSWERS["photosynthesis"]

        elif "artificial intelligence" in q:
            return REFERENCE_ANSWERS["artificial intelligence"]

        elif "telephone" in q:
            return REFERENCE_ANSWERS["telephone"]

        elif "water cycle" in q:
            return REFERENCE_ANSWERS["water cycle"]

        elif "machine learning" in q:
            return REFERENCE_ANSWERS["machine learning"]

        elif "malaria" in q:
            return REFERENCE_ANSWERS["malaria"]

        return None

    # -----------------------------------------
    # Main Evaluation
    # -----------------------------------------
    @staticmethod
    def process_request(request):

        logger.info("Evaluation Started")

        # -----------------------------------------
        # Retrieve Supporting Documents
        # -----------------------------------------
        retrieved_docs = retrieve_documents(request.question)

        # -----------------------------------------
        # Knowledge Evaluation (IMPROVED)
        # -----------------------------------------
        reference = EvaluationService.get_reference_answer(request.question)

        if reference:
            knowledge_result = KnowledgeAgent.evaluate(
    request.response,
    [{"context": reference}]
)
        else:
            knowledge_result = KnowledgeAgent.evaluate(
                request.response,
                retrieved_docs
            )

        # -----------------------------------------
        # Hallucination Evaluation
        # -----------------------------------------
        hallucination_result = HallucinationAgent.evaluate(
            request.response,
            retrieved_docs
        )

        # -----------------------------------------
        # Relevance Evaluation
        # -----------------------------------------
        relevance_result = RelevanceJudgeAgent.evaluate(
            question=request.question,
            response=request.response,
            retrieved_docs=retrieved_docs
        )

        # -----------------------------------------
        # Completeness Evaluation
        # -----------------------------------------
        completeness_result = CompletenessAgent.evaluate(
            request.question,
            request.response,
            retrieved_docs
        )

        # -----------------------------------------
        # Final Score (FIXED ARGUMENTS)
        # -----------------------------------------
        final_result = ScoringService.calculate_final_score(
            knowledge_result["knowledge_score"],
            hallucination_result["hallucination_score"],  # ✅ FIXED
            relevance_result["relevance_score"],
            completeness_result["completeness_score"]
        )

        logger.info("Evaluation Completed")

        # -----------------------------------------
        # Return Response
        # -----------------------------------------
        return {
            "question": request.question,
            "response": request.response,
            "timestamp": get_current_timestamp(),
            "retrieved_documents": retrieved_docs,
            "knowledge": knowledge_result,
            "hallucination": hallucination_result,
            "relevance": relevance_result,
            "completeness": completeness_result,
            "final_result": final_result
        }