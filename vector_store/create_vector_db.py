"""
create_vector_db.py

Purpose:
---------
Creates a ChromaDB vector database using the
generated embeddings from the Knowledge Base.

Input:
-------
embeddings/knowledge_base_embeddings.json

Output:
--------
vector_store/chroma_db/
"""

import json
from pathlib import Path
import chromadb
from chromadb.config import Settings


# ---------------------------------------------------
# Project Paths
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EMBEDDINGS_PATH = (
    PROJECT_ROOT /
    "embeddings" /
    "knowledge_base_embeddings.json"
)

CHROMA_DB_PATH = (
    PROJECT_ROOT /
    "vector_store" /
    "chroma_db"
)


# ---------------------------------------------------
# Create Chroma Client
# ---------------------------------------------------

client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH),
    settings=Settings(anonymized_telemetry=False)
)


# ---------------------------------------------------
# Delete Existing Collection (Optional)
# ---------------------------------------------------

try:
    client.delete_collection("knowledge_base")
    print("Existing collection deleted.")
except:
    pass


# ---------------------------------------------------
# Create Collection
# ---------------------------------------------------

collection = client.create_collection(
    name="knowledge_base"
)

print("Collection created successfully.\n")


# ---------------------------------------------------
# Load Embeddings
# ---------------------------------------------------

print("Loading embeddings...")

with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as file:
    records = json.load(file)

print(f"Loaded {len(records)} records.\n")


# ---------------------------------------------------
# Insert Records
# ---------------------------------------------------

print("Storing embeddings into ChromaDB...\n")

BATCH_SIZE = 500

for start in range(0, len(records), BATCH_SIZE):

    batch = records[start:start + BATCH_SIZE]

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for record in batch:

        ids.append(str(record["chunk_id"]))

        embeddings.append(record["embedding"])

        documents.append(record["context_chunk"])

        metadatas.append({

            "question": record["question"],

            "reference_answer": record["reference_answer"],

            "dataset": record["dataset"]

        })

    collection.add(

        ids=ids,

        embeddings=embeddings,

        documents=documents,

        metadatas=metadatas

    )

    print(f"Stored {min(start + BATCH_SIZE, len(records))} / {len(records)}")


print("\n======================================")
print("Vector Database Created Successfully")
print("======================================")

print(f"\nCollection Name : knowledge_base")

print(f"Database Location :\n{CHROMA_DB_PATH}")