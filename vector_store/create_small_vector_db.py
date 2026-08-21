from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from datasets import load_from_disk


# ---------------------------------------------------
# Paths
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SMALL_DB_PATH = (
    PROJECT_ROOT /
    "vector_store" /
    "chroma_db_small"
)


# ---------------------------------------------------
# Load datasets
# ---------------------------------------------------

print("Loading datasets...")

squad = load_from_disk(
    str(PROJECT_ROOT / "datasets" / "squad")
)

truthfulqa = load_from_disk(
    str(PROJECT_ROOT / "datasets" / "truthfulqa")
)

squad_validation = squad["validation"]
truthfulqa_validation = truthfulqa["validation"]

print(f"SQuAD validation : {len(squad_validation)}")
print(f"TruthfulQA       : {len(truthfulqa_validation)}")


# ---------------------------------------------------
# Prepare records
# ---------------------------------------------------

records = []


# SQuAD
for i, item in enumerate(squad_validation):

    answers = item["answers"]["text"]

    reference_answer = (
        answers[0]
        if answers
        else ""
    )

    records.append({
        "id": f"squad_{i}",
        "context": item["context"],
        "question": item["question"],
        "reference_answer": reference_answer,
        "dataset": "SQuAD"
    })


# TruthfulQA
for i, item in enumerate(truthfulqa_validation):

    question = item["question"]
    reference_answer = item["best_answer"]

    context = (
        f"Question: {question}\n"
        f"Correct Answer: {reference_answer}"
    )

    records.append({
        "id": f"truthfulqa_{i}",
        "context": context,
        "question": question,
        "reference_answer": reference_answer,
        "dataset": "TruthfulQA"
    })


print(f"\nTotal records: {len(records)}")


# ---------------------------------------------------
# Create ChromaDB
# ---------------------------------------------------

print("\nCreating small ChromaDB...")

client = chromadb.PersistentClient(
    path=str(SMALL_DB_PATH)
)

try:
    client.delete_collection("knowledge_base")
    print("Existing small collection deleted.")
except Exception:
    pass

collection = client.create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
print("Collection created.")


# ---------------------------------------------------
# Load LOCAL embedding model
# ---------------------------------------------------

print("\nLoading local embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Local embedding model loaded.")


# ---------------------------------------------------
# Generate embeddings and insert
# ---------------------------------------------------

BATCH_SIZE = 128

total = len(records)

print("\nStarting embedding generation...\n")


for start in range(0, total, BATCH_SIZE):

    batch = records[
        start:start + BATCH_SIZE
    ]

    texts = [
    f"Question: {record['question']}\n"
    f"Context: {record['context']}"
    for record in batch
]

    # Local embedding generation
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True
    ).tolist()

    ids = [
        record["id"]
        for record in batch
    ]

    documents = [
        record["context"]
        for record in batch
    ]

    metadatas = [
        {
            "question": record["question"],
            "reference_answer": record["reference_answer"],
            "dataset": record["dataset"]
        }
        for record in batch
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    processed = min(
        start + BATCH_SIZE,
        total
    )

    print(
        f"Stored {processed} / {total}"
    )


# ---------------------------------------------------
# Finished
# ---------------------------------------------------

print("\n======================================")
print("SMALL VECTOR DATABASE CREATED")
print("======================================")

print(f"Collection : knowledge_base")
print(f"Records    : {collection.count()}")
print(f"Location   : {SMALL_DB_PATH}")