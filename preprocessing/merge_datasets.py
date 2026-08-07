"""
merge_datasets.py

Purpose:
---------
Merge all cleaned datasets into a single
knowledge base for RAG retrieval.
"""

import json
from pathlib import Path

# ---------------------------------------------------
# Project Paths
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLEANED_DATASET = PROJECT_ROOT / "datasets" / "cleaned_dataset.json"

KNOWLEDGE_BASE = PROJECT_ROOT / "datasets" / "knowledge_base.json"


# ---------------------------------------------------
# Merge Dataset
# ---------------------------------------------------

def merge():

    with open(CLEANED_DATASET, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"Loaded {len(data)} records.")

    # Future datasets can also be merged here

    with open(KNOWLEDGE_BASE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"\nKnowledge Base created successfully.")
    print(f"Saved at : {KNOWLEDGE_BASE}")


# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":
    merge()