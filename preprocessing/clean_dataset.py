"""
clean_dataset.py

Purpose:
---------
Loads the downloaded datasets and converts them into
a common format that will later be used for RAG.

Output Columns

question
reference_answer
context
dataset
"""

from pathlib import Path
from datasets import load_from_disk
import pandas as pd


# ---------------------------------------------------
# Paths
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SQUAD_PATH = PROJECT_ROOT / "datasets" / "squad"
TRUTHFULQA_PATH = PROJECT_ROOT / "datasets" / "truthfulqa"

RESULT_PATH = PROJECT_ROOT / "datasets" / "cleaned_dataset.json"


# ---------------------------------------------------
# Clean SQuAD
# ---------------------------------------------------

def clean_squad():

    print("Cleaning SQuAD...")

    squad = load_from_disk(str(SQUAD_PATH))

    cleaned_records = []

    for sample in squad["train"]:

        question = sample["question"]

        context = sample["context"]

        answer = ""

        if len(sample["answers"]["text"]) > 0:
            answer = sample["answers"]["text"][0]

        cleaned_records.append({

            "question": question,

            "reference_answer": answer,

            "context": context,

            "dataset": "SQuAD"

        })

    print(f"SQuAD Records : {len(cleaned_records)}")

    return cleaned_records


# ---------------------------------------------------
# Clean TruthfulQA
# ---------------------------------------------------

def clean_truthfulqa():

    print("Cleaning TruthfulQA...")

    truthfulqa = load_from_disk(str(TRUTHFULQA_PATH))

    cleaned_records = []

    for sample in truthfulqa["validation"]:

        question = sample["question"]

        answer = sample["best_answer"]

        cleaned_records.append({

            "question": question,

            "reference_answer": answer,

            "context": "",

            "dataset": "TruthfulQA"

        })

    print(f"TruthfulQA Records : {len(cleaned_records)}")

    return cleaned_records


# ---------------------------------------------------
# Main
# ---------------------------------------------------

def main():

    squad_records = clean_squad()

    truthful_records = clean_truthfulqa()

    all_records = squad_records + truthful_records

    df = pd.DataFrame(all_records)

    df.to_json(
    RESULT_PATH,
    orient="records",
    indent=4
)

    print("\nDataset cleaned successfully.")

    print(f"Total Records : {len(df)}")

    print(f"Saved to : {RESULT_PATH}")

if __name__ == "__main__":
    main()