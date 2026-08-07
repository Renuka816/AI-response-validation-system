"""
explore_datasets.py

Purpose:
---------
Loads the locally saved datasets and displays
their structure, columns, and sample records.

This helps us understand the data before preprocessing.
"""

from pathlib import Path
from datasets import load_from_disk


# ---------------------------------------------------
# Project Paths
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SQUAD_PATH = PROJECT_ROOT / "datasets" / "squad"
TRUTHFULQA_PATH = PROJECT_ROOT / "datasets" / "truthfulqa"


# ---------------------------------------------------
# Explore SQuAD
# ---------------------------------------------------

def explore_squad():

    print("\n" + "=" * 60)
    print("SQuAD DATASET")
    print("=" * 60)

    squad = load_from_disk(str(SQUAD_PATH))

    print("\nDataset Splits:")
    print(squad)

    print("\nColumns:")
    print(squad["train"].column_names)

    print("\nNumber of Training Samples:")
    print(len(squad["train"]))

    print("\nSample Record:\n")

    sample = squad["train"][0]

    for key, value in sample.items():
        print(f"{key}:\n{value}\n")


# ---------------------------------------------------
# Explore TruthfulQA
# ---------------------------------------------------

def explore_truthfulqa():

    print("\n" + "=" * 60)
    print("TRUTHFULQA DATASET")
    print("=" * 60)

    truthfulqa = load_from_disk(str(TRUTHFULQA_PATH))

    print("\nDataset Splits:")
    print(truthfulqa)

    print("\nColumns:")
    print(truthfulqa["validation"].column_names)

    print("\nNumber of Validation Samples:")
    print(len(truthfulqa["validation"]))

    print("\nSample Record:\n")

    sample = truthfulqa["validation"][0]

    for key, value in sample.items():
        print(f"{key}:\n{value}\n")


# ---------------------------------------------------
# Main
# ---------------------------------------------------

def main():

    try:

        explore_squad()

        explore_truthfulqa()

    except Exception as e:

        print("\nError while loading datasets.")
        print(e)


if __name__ == "__main__":
    main()