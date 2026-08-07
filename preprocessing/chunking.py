"""
chunking.py

Purpose:
---------
Reads the merged knowledge base and splits
the context into smaller chunks for efficient
embedding generation and RAG retrieval.

Output:
--------
datasets/chunked_knowledge_base.json
"""

import json
from pathlib import Path


# ---------------------------------------------------
# Project Paths
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "datasets" / "knowledge_base.json"

OUTPUT_PATH = PROJECT_ROOT / "datasets" / "chunked_knowledge_base.json"


# ---------------------------------------------------
# Chunk Settings
# ---------------------------------------------------

CHUNK_SIZE = 150          # Number of words per chunk
OVERLAP = 30              # Overlap between chunks


# ---------------------------------------------------
# Chunk Function
# ---------------------------------------------------

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):

    if not text:
        return []

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------
# Main
# ---------------------------------------------------

def main():

    print("\nLoading Knowledge Base...")

    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:

        records = json.load(file)

    print(f"Loaded {len(records)} records.")

    chunked_records = []

    chunk_id = 1

    for record in records:

        context = record.get("context", "")

        chunks = chunk_text(context)

        # TruthfulQA has empty context.
        # Use reference answer instead.
        if len(chunks) == 0:

            chunks = [record["reference_answer"]]

        for chunk in chunks:

            chunked_records.append({

                "chunk_id": chunk_id,

                "question": record["question"],

                "reference_answer": record["reference_answer"],

                "context_chunk": chunk,

                "dataset": record["dataset"]

            })

            chunk_id += 1

    print(f"\nGenerated {len(chunked_records)} chunks.")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:

        json.dump(chunked_records, file, indent=4, ensure_ascii=False)

    print("\nChunked Knowledge Base saved successfully.")

    print(f"\nSaved to:\n{OUTPUT_PATH}")


# ---------------------------------------------------
# Run
# ---------------------------------------------------

if __name__ == "__main__":

    main()