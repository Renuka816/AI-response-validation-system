import json
import os


class EvaluationHistory:

    FILE_PATH = "backend/data/evaluation_history.json"

    # -----------------------------------------
    # Load existing evaluations
    # -----------------------------------------
    @staticmethod
    def get_all():

        if not os.path.exists(
            EvaluationHistory.FILE_PATH
        ):
            return []

        try:

            with open(
                EvaluationHistory.FILE_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception:

            return []

    # -----------------------------------------
    # Save one evaluation
    # -----------------------------------------
    @staticmethod
    def add(evaluation):

        evaluations = EvaluationHistory.get_all()

        evaluations.append(evaluation)

        os.makedirs(
            os.path.dirname(
                EvaluationHistory.FILE_PATH
            ),
            exist_ok=True
        )

        with open(
            EvaluationHistory.FILE_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                evaluations,
                file,
                indent=4
            )

    # -----------------------------------------
    # Save multiple evaluations
    # -----------------------------------------
    @staticmethod
    def add_many(evaluations):

        existing = EvaluationHistory.get_all()

        existing.extend(evaluations)

        os.makedirs(
            os.path.dirname(
                EvaluationHistory.FILE_PATH
            ),
            exist_ok=True
        )

        with open(
            EvaluationHistory.FILE_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                existing,
                file,
                indent=4
            )