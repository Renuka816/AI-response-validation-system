"""
download_datasets.py

Purpose:
--------
Downloads the required datasets from Hugging Face and stores
them locally for building the Knowledge Base.

Datasets:
1. SQuAD
2. TruthfulQA

Author: Renuka Meesala
"""

from pathlib import Path
from datasets import load_dataset


# -------------------------------------------------------
# Project Paths
# -------------------------------------------------------

# AI_Response_Quality_Evaluator/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASETS_DIR = PROJECT_ROOT / "datasets"
SQUAD_DIR = DATASETS_DIR / "squad"
TRUTHFULQA_DIR = DATASETS_DIR / "truthfulqa"


# -------------------------------------------------------
# Create folders if they don't exist
# -------------------------------------------------------

SQUAD_DIR.mkdir(parents=True, exist_ok=True)
TRUTHFULQA_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------
# Download SQuAD
# -------------------------------------------------------

def download_squad():
    print("\nDownloading SQuAD Dataset...")

    squad = load_dataset("squad")

    squad.save_to_disk(str(SQUAD_DIR))

    print("SQuAD downloaded successfully.")

    print(f"Train Samples : {len(squad['train'])}")
    print(f"Validation Samples : {len(squad['validation'])}")


# -------------------------------------------------------
# Download TruthfulQA
# -------------------------------------------------------

def download_truthfulqa():
    print("\nDownloading TruthfulQA Dataset...")

    truthfulqa = load_dataset("truthful_qa", "generation")

    truthfulqa.save_to_disk(str(TRUTHFULQA_DIR))

    print("TruthfulQA downloaded successfully.")

    print(f"Validation Samples : {len(truthfulqa['validation'])}")


# -------------------------------------------------------
# Main Function
# -------------------------------------------------------

def main():

    print("=" * 50)
    print("Downloading Knowledge Base Datasets")
    print("=" * 50)

    try:
        download_squad()
        download_truthfulqa()

        print("\nAll datasets downloaded successfully.")

    except Exception as e:
        print("\nError while downloading datasets.")
        print(e)


if __name__ == "__main__":
    main()