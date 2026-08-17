import os
import sys
import unittest
import pandas as pd
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.models.request_model import EvaluationRequest
from backend.services.evaluation_service import EvaluationService
from backend.services.rag_service import retrieve_documents
from backend.services.scoring_service import ScoringService
from backend.services.report_generator import generate_evaluation_report
from backend.database.database import (
    init_database,
    save_evaluation,
    get_dashboard_summary,
    get_dashboard_evaluations,
    get_quality_trends
)

class TestEndToEndSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize database before running E2E suite"""
        init_database()

    def test_01_rag_retrieval(self):
        """Verify RAG document retrieval module"""
        question = "What causes malaria?"
        docs = retrieve_documents(question)
        self.assertIsInstance(docs, list)

    def test_02_single_evaluation_workflow(self):
        """Verify end-to-end single evaluation workflow"""
        request = EvaluationRequest(
            question="What causes malaria?",
            response="Malaria is caused by Plasmodium parasites transmitted by infected Anopheles mosquitoes.",
            model="GPT-4o Test",
            dataset="E2E Unit Test"
        )
        
        result = EvaluationService.process_request(request)
        
        self.assertIn("accuracy", result)
        self.assertIn("hallucination", result)
        self.assertIn("relevance", result)
        self.assertIn("completeness", result)
        self.assertIn("final_result", result)
        
        self.assertGreaterEqual(result["final_result"]["final_score"], 0)
        self.assertLessEqual(result["final_result"]["final_score"], 100)

    def test_03_scoring_service_math(self):
        """Verify weighted scoring calculation logic"""
        res = ScoringService.calculate_final_score(
            knowledge=90.0,
            hallucination=0.0,
            relevance=85.0,
            completeness=80.0
        )
        
        final_score = res["final_score"]
        grade = res["grade"]
        reason = res["reason"]
        
        self.assertGreater(final_score, 80.0)
        self.assertIn(grade, ["Excellent", "Good", "Average", "Poor", "Pass", "Needs Review", "Fail"])
        self.assertIsInstance(reason, str)

    def test_04_database_and_dashboard_integration(self):
        """Verify saving evaluation to SQLite database and dashboard metric computation"""
        save_evaluation(
            question="What is photosythesis?",
            response="Photosynthesis is the process by which green plants convert light into chemical energy.",
            accuracy_score=95.0,
            relevance_score=90.0,
            hallucination_score=100.0,
            completeness_score=85.0,
            final_score=92.5,
            grade="Excellent",
            timestamp="2026-08-13 00:00:00",
            evaluation_mode="single",
            model="GPT-4o Test",
            dataset="E2E Unit Test"
        )
        
        summary = get_dashboard_summary(model="GPT-4o Test")
        self.assertGreaterEqual(summary["total_evaluations"], 1)
        self.assertIn("average_score", summary)
        
        evaluations = get_dashboard_evaluations(model="GPT-4o Test")
        self.assertGreaterEqual(len(evaluations), 1)

    def test_05_batch_csv_evaluation(self):
        """Verify batch CSV evaluation data processing"""
        data = {
            "question": [
                "What is artificial intelligence?",
                "How does gravity work?"
            ],
            "response": [
                "AI refers to computer systems capable of performing human tasks.",
                "Gravity is a fundamental force of attraction between masses."
            ],
            "model": ["Model-A", "Model-B"],
            "dataset": ["BatchTest", "BatchTest"]
        }
        df = pd.DataFrame(data)
        
        results = []
        for _, row in df.iterrows():
            req = EvaluationRequest(
                question=row["question"],
                response=row["response"],
                model=row["model"],
                dataset=row["dataset"]
            )
            eval_res = EvaluationService.process_request(req)
            results.append(eval_res)
            
        self.assertEqual(len(results), 2)

    def test_06_report_generation(self):
        """Verify ReportLab PDF generation service"""
        dummy_evaluations = [
            {
                "id": 1,
                "question": "What is machine learning?",
                "response": "ML is a subset of AI enabling systems to learn from data.",
                "accuracy_score": 90.0,
                "relevance_score": 95.0,
                "hallucination_score": 100.0,
                "completeness_score": 85.0,
                "final_score": 92.5,
                "grade": "Excellent",
                "hallucination_detected": 0,
                "timestamp": "2026-08-13 00:00:00",
                "evaluation_mode": "single",
                "model": "GPT-4o",
                "dataset": "Test Set"
            }
        ]
        
        pdf_path = generate_evaluation_report(dummy_evaluations)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(str(pdf_path).endswith(".pdf"))

    def test_07_invalid_input_handling(self):
        """Verify error handling on invalid / empty inputs"""
        with self.assertRaises(Exception):
            EvaluationRequest(
                question="",
                response="",
            )

if __name__ == "__main__":
    unittest.main()
