from services.rag_service import retrieve_documents
from services.knowledge_agent import KnowledgeAgent
from services.hallucination_agent import HallucinationAgent
from services.relevance_agent import RelevanceAgent
from services.completeness_agent import CompletenessAgent
from services.scoring_service import ScoringService


# --------------------------------------------------
# Test Input
# --------------------------------------------------

question = "What causes malaria?"

ai_response = (
    "Malaria is caused by Plasmodium parasites "
    "that are transmitted through the bites of infected Anopheles mosquitoes."
)


# --------------------------------------------------
# Retrieve Documents
# --------------------------------------------------

print("\nRetrieving supporting documents...\n")

documents = retrieve_documents(question)

print(f"Retrieved {len(documents)} documents.\n")


# --------------------------------------------------
# Knowledge Agent
# --------------------------------------------------

knowledge_result = KnowledgeAgent.evaluate(
    ai_response,
    documents
)

print("=" * 60)
print("Knowledge Agent")
print("=" * 60)
print(knowledge_result)


# --------------------------------------------------
# Hallucination Agent
# --------------------------------------------------

hallucination_result = HallucinationAgent.evaluate(
    ai_response,
    documents
)

print("\n" + "=" * 60)
print("Hallucination Agent")
print("=" * 60)
print(hallucination_result)


# --------------------------------------------------
# Relevance Agent
# --------------------------------------------------

relevance_result = RelevanceAgent.evaluate(
    question,
    ai_response
)

print("\n" + "=" * 60)
print("Relevance Agent")
print("=" * 60)
print(relevance_result)


# --------------------------------------------------
# Completeness Agent
# --------------------------------------------------

completeness_result = CompletenessAgent.evaluate(
    ai_response,
    documents
)

print("\n" + "=" * 60)
print("Completeness Agent")
print("=" * 60)
print(completeness_result)


# --------------------------------------------------
# Final Score
# --------------------------------------------------

final_result = ScoringService.calculate_final_score(

    knowledge_result["knowledge_score"],

    hallucination_result["hallucination_score"],

    relevance_result["relevance_score"],

    completeness_result["completeness_score"]

)

print("\n" + "=" * 60)
print("Final Evaluation")
print("=" * 60)
print(final_result)