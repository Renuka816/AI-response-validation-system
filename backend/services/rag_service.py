from pathlib import Path

import chromadb


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHROMA_DB_PATH = PROJECT_ROOT / "vector_store" / "chroma_db"


# --------------------------------------------------
# Load model (only once)
# --------------------------------------------------
from backend.services.embedding_service import EmbeddingService

model = EmbeddingService.get_model()


# --------------------------------------------------
# Connect to ChromaDB
# --------------------------------------------------

client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

collection = client.get_collection("knowledge_base")

print("Connected to ChromaDB.")


# --------------------------------------------------
# Retrieve documents
# --------------------------------------------------

def retrieve_documents(question: str, top_k: int = 5):

    query_embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_documents = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved_documents.append({

            "context": document,

            "question": metadata.get("question"),

            "reference_answer": metadata.get("reference_answer"),

            "dataset": metadata.get("dataset"),

            "distance": round(distance, 4)

        })

    return retrieved_documents