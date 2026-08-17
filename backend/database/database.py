import sqlite3
from pathlib import Path


# =========================================================
# Database Location
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_DIR = BASE_DIR / "backend" / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "evaluations.db"


# =========================================================
# Database Connection
# =========================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# Initialize Database
# =========================================================

def init_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            question TEXT NOT NULL,

            response TEXT NOT NULL,

            accuracy_score REAL DEFAULT 0,

            relevance_score REAL DEFAULT 0,

            hallucination_score REAL DEFAULT 0,

            completeness_score REAL DEFAULT 0,

            final_score REAL DEFAULT 0,

            grade TEXT,

            hallucination_detected INTEGER DEFAULT 0,

            timestamp TEXT,

            evaluation_mode TEXT DEFAULT 'single',

            model TEXT,

            dataset TEXT

        )
        """
    )

    connection.commit()
    connection.close()


# =========================================================
# Save Evaluation
# =========================================================

def save_evaluation(
    question,
    response,
    accuracy_score,
    relevance_score,
    hallucination_score,
    completeness_score,
    final_score,
    grade,
    timestamp,
    evaluation_mode="single",
    model=None,
    dataset=None
):

    connection = get_connection()
    cursor = connection.cursor()

    hallucination_detected = (
        1 if float(hallucination_score) < 50 else 0
    )

    cursor.execute(
        """
        INSERT INTO evaluations (

            question,
            response,
            accuracy_score,
            relevance_score,
            hallucination_score,
            completeness_score,
            final_score,
            grade,
            hallucination_detected,
            timestamp,
            evaluation_mode,
            model,
            dataset

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            question,
            response,
            accuracy_score,
            relevance_score,
            hallucination_score,
            completeness_score,
            final_score,
            grade,
            hallucination_detected,
            timestamp,
            evaluation_mode,
            model,
            dataset
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# Fetch All Evaluations
# =========================================================

def get_all_evaluations():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM evaluations
        ORDER BY id ASC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# =========================================================
# Dashboard Summary
# =========================================================

def get_dashboard_summary(
    evaluation_mode=None,
    model=None,
    dataset=None,
    date_from=None,
    date_to=None
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT

            COUNT(*) AS total_evaluations,

            SUM(
                CASE
                    WHEN grade = 'Good'
                    THEN 1 ELSE 0
                END
            ) AS pass_count,

            SUM(
                CASE
                    WHEN grade = 'Average'
                    THEN 1 ELSE 0
                END
            ) AS needs_improvement_count,

            SUM(
                CASE
                    WHEN grade = 'Poor'
                    THEN 1 ELSE 0
                END
            ) AS fail_count,

            AVG(final_score) AS average_score,

            AVG(accuracy_score) AS average_accuracy,

            AVG(relevance_score) AS average_relevance,

            AVG(completeness_score) AS average_completeness,

            AVG(hallucination_score) AS average_hallucination,

            SUM(hallucination_detected) AS hallucination_count

        FROM evaluations

        WHERE 1 = 1
    """

    parameters = []

    if evaluation_mode:
        query += " AND evaluation_mode = ?"
        parameters.append(evaluation_mode)

    if model:
        query += " AND model = ?"
        parameters.append(model)

    if dataset:
        query += " AND dataset = ?"
        parameters.append(dataset)

    if date_from:
        query += " AND date(timestamp) >= date(?)"
        parameters.append(date_from)

    if date_to:
        query += " AND date(timestamp) <= date(?)"
        parameters.append(date_to)

    cursor.execute(query, parameters)

    row = cursor.fetchone()

    connection.close()

    if not row or row["total_evaluations"] == 0:

        return {
            "total_evaluations": 0,
            "pass_count": 0,
            "needs_improvement_count": 0,
            "fail_count": 0,
            "average_score": 0,
            "average_accuracy": 0,
            "average_relevance": 0,
            "average_completeness": 0,
            "average_hallucination": 0,
            "hallucination_count": 0,
            "hallucination_frequency": 0
        }

    total = row["total_evaluations"] or 0
    hallucinations = row["hallucination_count"] or 0

    hallucination_frequency = (
        (hallucinations / total) * 100
        if total > 0
        else 0
    )

    return {

        "total_evaluations": total,

        "pass_count":
            row["pass_count"] or 0,

        "needs_improvement_count":
            row["needs_improvement_count"] or 0,

        "fail_count":
            row["fail_count"] or 0,

        "average_score":
            round(row["average_score"] or 0, 2),

        "average_accuracy":
            round(row["average_accuracy"] or 0, 2),

        "average_relevance":
            round(row["average_relevance"] or 0, 2),

        "average_completeness":
            round(row["average_completeness"] or 0, 2),

        "average_hallucination":
            round(row["average_hallucination"] or 0, 2),

        "hallucination_count":
            hallucinations,

        "hallucination_frequency":
            round(hallucination_frequency, 2)
    }


# =========================================================
# Dashboard Evaluations
# =========================================================

def get_dashboard_evaluations(
    evaluation_mode=None,
    model=None,
    dataset=None,
    date_from=None,
    date_to=None
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT

            id,
            question,
            response,
            accuracy_score,
            relevance_score,
            hallucination_score,
            completeness_score,
            final_score,
            grade,
            hallucination_detected,
            timestamp,
            evaluation_mode,
            model,
            dataset

        FROM evaluations

        WHERE 1 = 1
    """

    parameters = []

    if evaluation_mode:
        query += " AND evaluation_mode = ?"
        parameters.append(evaluation_mode)

    if model:
        query += " AND model = ?"
        parameters.append(model)

    if dataset:
        query += " AND dataset = ?"
        parameters.append(dataset)

    if date_from:
        query += " AND date(timestamp) >= date(?)"
        parameters.append(date_from)

    if date_to:
        query += " AND date(timestamp) <= date(?)"
        parameters.append(date_to)

    query += " ORDER BY id DESC"

    cursor.execute(query, parameters)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# =========================================================
# Quality Trends
# =========================================================

def get_quality_trends(
    evaluation_mode=None,
    model=None,
    dataset=None,
    date_from=None,
    date_to=None
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT

            timestamp,
            final_score,
            accuracy_score,
            relevance_score,
            completeness_score

        FROM evaluations

        WHERE 1 = 1
    """

    parameters = []

    if evaluation_mode:
        query += " AND evaluation_mode = ?"
        parameters.append(evaluation_mode)

    if model:
        query += " AND model = ?"
        parameters.append(model)

    if dataset:
        query += " AND dataset = ?"
        parameters.append(dataset)

    if date_from:
        query += " AND date(timestamp) >= date(?)"
        parameters.append(date_from)

    if date_to:
        query += " AND date(timestamp) <= date(?)"
        parameters.append(date_to)

    query += " ORDER BY id ASC"

    cursor.execute(query, parameters)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]