from pathlib import Path
import chromadb

from backend.utils.embedding_model import get_embedding_model


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHROMA_DB_PATH = PROJECT_ROOT / "vector_store" / "chroma_db_small"


# --------------------------------------------------
# Lazy-loaded resources
# --------------------------------------------------

_model = None
_client = None
_collection = None


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

def get_model():

    global _model

    if _model is None:

        print("Loading embedding model...")

        _model = get_embedding_model()

        print("Embedding model ready.")

    return _model


# --------------------------------------------------
# Connect to ChromaDB
# --------------------------------------------------

def get_collection():

    global _client
    global _collection

    if _collection is None:

        print("Connecting to ChromaDB...")
        print("Chroma path:", CHROMA_DB_PATH)
        print("Chroma path exists:", CHROMA_DB_PATH.exists())

        if not CHROMA_DB_PATH.exists():
            raise RuntimeError(
                f"ChromaDB path does not exist: {CHROMA_DB_PATH}"
            )

        sqlite_file = CHROMA_DB_PATH / "chroma.sqlite3"

        print("SQLite exists:", sqlite_file.exists())

        _client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH)
        )

        collections = _client.list_collections()

        print("RENDER CHROMA COLLECTIONS:", collections)

        if not collections:
            raise RuntimeError(
                "ChromaDB loaded successfully, but no collections were found."
            )

        try:
            _collection = _client.get_collection(
                name="knowledge_base"
            )

        except Exception as e:

            raise RuntimeError(
                f"Collection 'knowledge_base' does not exist. "
                f"Available collections: {collections}"
            ) from e

        print("Connected to ChromaDB.")
        print("Collection count:", _collection.count())

    return _collection


# --------------------------------------------------
# Retrieve documents
# --------------------------------------------------

def retrieve_documents(
    question: str,
    top_k: int = 5
):

    model = get_model()

    collection = get_collection()

    # ----------------------------------------------
    # Create query embedding
    # ----------------------------------------------

    query_embedding = model.encode(
        question
    )

    # ----------------------------------------------
    # Handle single embedding
    # ----------------------------------------------

    if hasattr(query_embedding, "tolist"):
        query_embedding = query_embedding.tolist()

    # ----------------------------------------------
    # Search ChromaDB
    # ----------------------------------------------

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