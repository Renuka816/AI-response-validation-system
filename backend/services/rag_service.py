from pathlib import Path
import chromadb

from backend.services.embedding_service import EmbeddingService


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHROMA_DB_PATH = PROJECT_ROOT / "vector_store" / "chroma_db"


# --------------------------------------------------
# Lazy-loaded resources
# --------------------------------------------------

_model = None
_client = None
_collection = None


# --------------------------------------------------
# Load embedding model only when required
# --------------------------------------------------

def get_model():

    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = EmbeddingService.get_model()
        print("Embedding model loaded.")

    return _model


# --------------------------------------------------
# Connect to ChromaDB only when required
# --------------------------------------------------

def get_collection():

    global _client
    global _collection

    if _collection is None:

        print("Connecting to ChromaDB...")

        _client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH)
        )

        _collection = _client.get_collection(
            "knowledge_base"
        )

        print("Connected to ChromaDB.")

    return _collection


# --------------------------------------------------
# Retrieve documents
# --------------------------------------------------

def retrieve_documents(
    question: str,
    top_k: int = 5
):

    # Load model only when retrieval is requested
    model = get_model()

    # Connect to ChromaDB only when retrieval is requested
    collection = get_collection()

    # Create query embedding
    query_embedding = model.encode(
        question
    ).tolist()

    # Search ChromaDB
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

            "question": metadata.get(
                "question"
            ),

            "reference_answer": metadata.get(
                "reference_answer"
            ),

            "dataset": metadata.get(
                "dataset"
            ),

            "distance": round(
                distance,
                4
            )
        })

    return retrieved_documents