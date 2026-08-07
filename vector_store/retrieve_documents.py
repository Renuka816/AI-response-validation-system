"""
retrieve_documents.py

Purpose:
---------
Retrieves the most relevant documents from ChromaDB
using semantic similarity search.

Input:
-------
User Query

Output:
--------
Top-K relevant chunks from the Knowledge Base.
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------
# Project Paths
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DB_PATH = (
    PROJECT_ROOT /
    "vector_store" /
    "chroma_db"
)


# ---------------------------------------------------
# Load Embedding Model
# ---------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.\n")


# ---------------------------------------------------
# Connect to ChromaDB
# ---------------------------------------------------

client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH),
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection("knowledge_base")

print("Connected to ChromaDB.\n")


# ---------------------------------------------------
# Retrieval Function
# ---------------------------------------------------

def retrieve_documents(query, top_k=5):

    print(f"\nSearching for:\n{query}\n")

    query_embedding = model.encode(query).tolist()

    results = collection.query(

        query_embeddings=[query_embedding],

        n_results=top_k

    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("=" * 70)
    print(f"Top {top_k} Retrieved Documents")
    print("=" * 70)

    for i in range(len(documents)):

        print(f"\nResult {i+1}")

        print("-" * 70)

        print(f"Similarity Distance : {distances[i]:.4f}")

        print(f"Dataset : {metadatas[i]['dataset']}")

        print(f"Question : {metadatas[i]['question']}")

        print(f"Reference Answer : {metadatas[i]['reference_answer']}")

        print(f"\nRetrieved Context:\n")

        print(documents[i])

        print("\n")


# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    query = input("Enter your question: ")

    retrieve_documents(query)