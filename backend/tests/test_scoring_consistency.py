import sys
import unittest
import numpy as np
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.models.request_model import EvaluationRequest
from backend.services.evaluation_service import EvaluationService

class TestScoringConsistency(unittest.TestCase):

    def test_scoring_consistency_across_iterations(self):
        """
        Validate agent scoring stability by executing the same evaluation query 3 times.
        Computes mean, standard deviation, and coefficient of variation for each dimension score.
        """
        test_request = EvaluationRequest(
            question="What is photosythesis and how does it work?",
            response="Photosynthesis is the biological process used by plants, algae, and certain bacteria to convert light energy into chemical energy stored in glucose.",
            model="GPT-4o Consistency Test",
            dataset="Consistency Validation Set"
        )

        iterations = 3
        accuracy_scores = []
        relevance_scores = []
        completeness_scores = []
        hallucination_scores = []
        final_scores = []
        grades = []

        print("\n" + "=" * 70)
        print("RUNNING SCORING CONSISTENCY VALIDATION (3 ITERATIONS)")
        print("=" * 70)

        for i in range(1, iterations + 1):
            result = EvaluationService.process_request(test_request)
            
            acc = result["accuracy"]["accuracy_score"]
            rel = result["relevance"]["relevance_score"]
            comp = result["completeness"]["completeness_score"]
            hal = result["hallucination"]["hallucination_score"]
            fin = result["final_result"]["final_score"]
            grd = result["final_result"]["grade"]

            accuracy_scores.append(acc)
            relevance_scores.append(rel)
            completeness_scores.append(comp)
            hallucination_scores.append(hal)
            final_scores.append(fin)
            grades.append(grd)

            print(f"Run #{i} -> Final Score: {fin:.2f}% | Grade: {grd} | Acc: {acc} | Rel: {rel} | Comp: {comp} | Hal: {hal}")

        # Compute Statistical Metrics
        metrics = {
            "Accuracy": accuracy_scores,
            "Relevance": relevance_scores,
            "Completeness": completeness_scores,
            "Hallucination": hallucination_scores,
            "Final Score": final_scores
        }

        print("\n" + "-" * 70)
        print(f"{'Metric':<18} | {'Mean Score':<12} | {'Std Dev (sigma)':<16} | {'Variance Coeff (%)':<20}")
        print("-" * 70)

        for name, scores in metrics.items():
            mean_val = float(np.mean(scores))
            std_val = float(np.std(scores))
            cv_val = (std_val / mean_val * 100.0) if mean_val > 0 else 0.0
            
            print(f"{name:<18} | {mean_val:<12.2f} | {std_val:<12.4f} | {cv_val:<24.2f}%")
            
            # Assert low standard deviation for deterministic scoring stability
            self.assertLessEqual(std_val, 15.0, f"Standard deviation too high for {name}: {std_val}")

        # Assert Grade consistency across runs
        self.assertEqual(len(set(grades)), 1, "Grade verdict fluctuated across identical runs.")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    unittest.main()
