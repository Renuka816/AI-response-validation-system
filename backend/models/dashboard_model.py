from pydantic import BaseModel
from typing import Optional


class DashboardSummary(BaseModel):

    total_evaluations: int

    pass_count: int

    needs_improvement_count: int

    fail_count: int

    average_accuracy: float

    average_relevance: float

    average_completeness: float

    hallucination_frequency: float


class DashboardEvaluation(BaseModel):

    id: int

    question: str

    final_score: float

    grade: str

    accuracy_score: float

    relevance_score: float

    hallucination_score: float

    completeness_score: float

    hallucination_detected: bool

    timestamp: Optional[str] = None

    evaluation_mode: Optional[str] = None

    model: Optional[str] = None

    dataset: Optional[str] = None