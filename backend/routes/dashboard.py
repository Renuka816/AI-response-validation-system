from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Optional
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)

from fastapi.responses import FileResponse

from backend.services.report_generator import (
    generate_evaluation_report
)

from backend.database.database import (
    get_dashboard_summary,
    get_dashboard_evaluations,
    get_quality_trends
)

router = APIRouter()


# =========================================================
# Dashboard Summary
# =========================================================

@router.get("/summary")
async def get_dashboard_summary_api(
    evaluation_mode: Optional[str] = None,
    model: Optional[str] = None,
    dataset: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):

    return get_dashboard_summary(
        evaluation_mode=evaluation_mode,
        model=model,
        dataset=dataset,
        date_from=date_from,
        date_to=date_to
    )


# =========================================================
# Dashboard Evaluations
# =========================================================

@router.get("/evaluations")
async def get_dashboard_evaluations_api(
    evaluation_mode: Optional[str] = None,
    model: Optional[str] = None,
    dataset: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):

    return get_dashboard_evaluations(
        evaluation_mode=evaluation_mode,
        model=model,
        dataset=dataset,
        date_from=date_from,
        date_to=date_to
    )


# =========================================================
# Quality Trends
# =========================================================

@router.get("/trends")
async def get_quality_trends_api(
    evaluation_mode: Optional[str] = None,
    model: Optional[str] = None,
    dataset: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):

    return get_quality_trends(
        evaluation_mode=evaluation_mode,
        model=model,
        dataset=dataset,
        date_from=date_from,
        date_to=date_to
    )


# =========================================================
# PDF REPORT HELPERS
# =========================================================

def safe_number(value):
    try:
        return round(float(value or 0), 2)
    except Exception:
        return 0


def create_recommendations(summary):
    """
    Generate improvement recommendations
    based on evaluation dimensions.
    """

    recommendations = []

    accuracy = safe_number(summary.get("average_accuracy"))
    relevance = safe_number(summary.get("average_relevance"))
    completeness = safe_number(summary.get("average_completeness"))
    hallucination = safe_number(summary.get("average_hallucination"))

    if accuracy < 70:
        recommendations.append(
            "Improve factual accuracy by strengthening reference-based "
            "verification and retrieval quality."
        )

    if relevance < 70:
        recommendations.append(
            "Improve response relevance by reducing unnecessary or "
            "off-topic information."
        )

    if completeness < 70:
        recommendations.append(
            "Improve completeness by ensuring that responses address "
            "all important aspects of the question."
        )

    if hallucination < 70:
        recommendations.append(
            "Reduce hallucinations by increasing grounding in retrieved "
            "reference documents and validating generated claims."
        )

    if not recommendations:
        recommendations.append(
            "Overall response quality is satisfactory. Continue monitoring "
            "accuracy, relevance, completeness and hallucination scores."
        )

    return recommendations


def build_score_chart(summary):
    """
    Creates a table-based visual score chart.
    """

    dimensions = [
        ("Accuracy", safe_number(summary.get("average_accuracy"))),
        ("Relevance", safe_number(summary.get("average_relevance"))),
        ("Completeness", safe_number(summary.get("average_completeness"))),
        ("Hallucination", safe_number(summary.get("average_hallucination")))
    ]

    rows = [
        [
            Paragraph(
                "<b>Dimension</b>",
                ParagraphStyle(
                    "header",
                    textColor=colors.white
                )
            ),
            Paragraph(
                "<b>Score</b>",
                ParagraphStyle(
                    "header2",
                    textColor=colors.white
                )
            ),
            Paragraph(
                "<b>Performance</b>",
                ParagraphStyle(
                    "header3",
                    textColor=colors.white
                )
            )
        ]
    ]

    for name, score in dimensions:

        if score >= 80:
            performance = "Excellent"
        elif score >= 70:
            performance = "Good"
        elif score >= 50:
            performance = "Needs Improvement"
        else:
            performance = "Poor"

        rows.append([
            name,
            f"{score:.2f}/100",
            performance
        ])

    table = Table(
        rows,
        colWidths=[
            2.2 * inch,
            1.4 * inch,
            2.4 * inch
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#334155")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CBD5E1")
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#F8FAFC")
            ),
            (
                "TEXTCOLOR",
                (0, 1),
                (-1, -1),
                colors.HexColor("#0F172A")
            ),
            (
                "ALIGN",
                (1, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    return table


# =========================================================
# PDF REPORT EXPORT
# =========================================================

@router.get("/report/pdf")
async def export_evaluation_report(
    evaluation_mode: Optional[str] = None,
    model: Optional[str] = None,
    dataset: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):

    summary = get_dashboard_summary(
        evaluation_mode=evaluation_mode,
        model=model,
        dataset=dataset,
        date_from=date_from,
        date_to=date_to
    )

    evaluations = get_dashboard_evaluations(
        evaluation_mode=evaluation_mode,
        model=model,
        dataset=dataset,
        date_from=date_from,
        date_to=date_to
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=14,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    story = []

    # =====================================================
    # TITLE
    # =====================================================

    story.append(
        Paragraph(
            "AI Response Validation System",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Multi-Agent RAG-Based Hallucination Detection & Response Evaluation",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            subtitle_style
        )
    )

    # =====================================================
    # PROJECT DETAILS
    # =====================================================

    story.append(
        Paragraph(
            "1. Project Details",
            section_style
        )
    )

    project_data = [
        ["Project", "AI Response Validation System"],
        [
            "Evaluation Architecture",
            "RAG + Multi-Agent Evaluation"
        ],
        [
            "Evaluation Dimensions",
            "Accuracy, Relevance, Completeness, Hallucination"
        ],
        [
            "Evaluation Mode",
            evaluation_mode if evaluation_mode else "All Modes"
        ],
        [
            "Model",
            model if model else "All Models"
        ],
        [
            "Dataset",
            dataset if dataset else "All Datasets"
        ],
        [
            "Date Range",
            f"{date_from or 'All'} to {date_to or 'All'}"
        ]
    ]

    project_table = Table(
        project_data,
        colWidths=[
            2.0 * inch,
            4.5 * inch
        ]
    )

    project_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CBD5E1")
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#E2E8F0")
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(project_table)
    story.append(Spacer(1, 15))

    # =====================================================
    # BATCH SUMMARY
    # =====================================================

    story.append(
        Paragraph(
            "2. Batch Evaluation Summary",
            section_style
        )
    )

    summary_data = [
        ["Metric", "Value"],
        [
            "Total Evaluations",
            str(summary.get("total_evaluations", 0))
        ],
        [
            "Average Score",
            f"{safe_number(summary.get('average_score'))}/100"
        ],
        [
            "Pass",
            str(summary.get("pass_count", 0))
        ],
        [
            "Needs Improvement",
            str(summary.get("needs_improvement_count", 0))
        ],
        [
            "Fail",
            str(summary.get("fail_count", 0))
        ],
        [
            "Hallucinations Detected",
            str(summary.get("hallucination_count", 0))
        ],
        [
            "Hallucination Frequency",
            f"{safe_number(summary.get('hallucination_frequency'))}%"
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            3.8 * inch,
            2.7 * inch
        ]
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#334155")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CBD5E1")
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#F8FAFC")
            ),
            (
                "ALIGN",
                (1, 0),
                (1, -1),
                "CENTER"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(summary_table)

    # =====================================================
    # DIMENSION BREAKDOWN
    # =====================================================

    story.append(
        Paragraph(
            "3. Dimension-wise Quality Scores",
            section_style
        )
    )

    story.append(
        build_score_chart(summary)
    )

    # =====================================================
    # OVERALL VERDICT
    # =====================================================

    story.append(
        Paragraph(
            "4. Overall Verdict",
            section_style
        )
    )

    total = summary.get("total_evaluations", 0)
    average_score = safe_number(
        summary.get("average_score")
    )

    if average_score >= 80:
        overall_verdict = "Excellent"
    elif average_score >= 70:
        overall_verdict = "Good"
    elif average_score >= 50:
        overall_verdict = "Needs Improvement"
    else:
        overall_verdict = "Poor"

    verdict_text = (
        f"The evaluation set contains <b>{total}</b> responses "
        f"with an average quality score of "
        f"<b>{average_score}/100</b>. "
        f"The overall evaluation verdict is "
        f"<b>{overall_verdict}</b>."
    )

    story.append(
        Paragraph(
            verdict_text,
            normal_style
        )
    )

    # =====================================================
    # INDIVIDUAL EVALUATIONS
    # =====================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "5. Individual Evaluation Results",
            section_style
        )
    )

    if not evaluations:

        story.append(
            Paragraph(
                "No evaluation results were found for the selected filters.",
                normal_style
            )
        )

    else:

        individual_data = [
            [
                "ID",
                "Question",
                "Accuracy",
                "Relevance",
                "Completeness",
                "Hallucination",
                "Overall",
                "Verdict"
            ]
        ]

        for item in evaluations:

            question = str(item.get("question", ""))

            if len(question) > 70:
                question = question[:67] + "..."

            individual_data.append([
                str(item.get("id", "")),
                Paragraph(question, small_style),
                str(safe_number(item.get("accuracy_score"))),
                str(safe_number(item.get("relevance_score"))),
                str(safe_number(item.get("completeness_score"))),
                str(safe_number(item.get("hallucination_score"))),
                str(safe_number(item.get("final_score"))),
                item.get("grade", "Unknown")
            ])

        individual_table = Table(
            individual_data,
            colWidths=[
                0.35 * inch,
                2.15 * inch,
                0.65 * inch,
                0.65 * inch,
                0.75 * inch,
                0.75 * inch,
                0.6 * inch,
                0.65 * inch
            ],
            repeatRows=1
        )

        individual_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#334155")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#CBD5E1")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.white
                ),
                (
                    "ALIGN",
                    (0, 1),
                    (0, -1),
                    "CENTER"
                ),
                (
                    "ALIGN",
                    (2, 1),
                    (-2, -1),
                    "CENTER"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        story.append(individual_table)

    # =====================================================
    # HALLUCINATED / FLAGGED RESPONSES
    # =====================================================

    story.append(
        Paragraph(
            "6. Hallucinated / Flagged Responses",
            section_style
        )
    )

    flagged = [
        item
        for item in evaluations
        if int(item.get("hallucination_detected", 0) or 0) == 1
    ]

    if not flagged:

        story.append(
            Paragraph(
                "No hallucinated responses were detected "
                "in the selected evaluation set.",
                normal_style
            )
        )

    else:

        # Group identical questions so the same question
        # does not appear repeatedly in the report.

        grouped_hallucinations = {}

        for item in flagged:

            question = str(
                item.get("question", "")
            ).strip()

            if question not in grouped_hallucinations:
                grouped_hallucinations[question] = []

            grouped_hallucinations[question].append(item)

        for index, (question, items) in enumerate(
            grouped_hallucinations.items(),
            start=1
        ):

            story.append(
                Paragraph(
                    f"<b>Flagged Question {index}</b>",
                    normal_style
                )
            )

            story.append(Spacer(1, 4))

            story.append(
                Paragraph(
                    f"<b>Question:</b> {question}",
                    small_style
                )
            )

            story.append(Spacer(1, 4))

            story.append(
                Paragraph(
                    f"<b>Occurrences:</b> {len(items)}",
                    small_style
                )
            )

            story.append(Spacer(1, 4))

            unique_responses = []

            for item in items:

                response = str(
                    item.get("response", "")
                ).strip()

                if response not in unique_responses:
                    unique_responses.append(response)

            for response_index, response in enumerate(
                unique_responses,
                start=1
            ):

                story.append(
                    Paragraph(
                        f"<b>Response {response_index}:</b> "
                        f"{response}",
                        small_style
                    )
                )

                story.append(Spacer(1, 4))

            scores = [
                safe_number(
                    item.get("hallucination_score")
                )
                for item in items
            ]

            average_flagged_score = (
                sum(scores) / len(scores)
                if scores
                else 0
            )

            story.append(
                Paragraph(
                    f"<b>Average Hallucination Score:</b> "
                    f"{safe_number(average_flagged_score)}/100",
                    small_style
                )
            )

            verdicts = set(
                str(item.get("grade", "N/A"))
                for item in items
            )

            story.append(
                Paragraph(
                    f"<b>Verdict:</b> "
                    f"{', '.join(verdicts)}",
                    small_style
                )
            )

            story.append(Spacer(1, 12))

    # =====================================================
    # VERDICT DISTRIBUTION
    # =====================================================

    story.append(
        Paragraph(
            "7. Evaluation Verdict Distribution",
            section_style
        )
    )

    pass_count = summary.get("pass_count", 0) or 0
    needs_improvement_count = (
        summary.get("needs_improvement_count", 0) or 0
    )
    fail_count = summary.get("fail_count", 0) or 0

    pass_percentage = (
        (pass_count / total) * 100
        if total else 0
    )

    needs_improvement_percentage = (
        (needs_improvement_count / total) * 100
        if total else 0
    )

    fail_percentage = (
        (fail_count / total) * 100
        if total else 0
    )

    verdict_data = [
        ["Verdict", "Count", "Percentage"],
        [
            "Pass",
            pass_count,
            f"{pass_percentage:.2f}%"
        ],
        [
            "Needs Improvement",
            needs_improvement_count,
            f"{needs_improvement_percentage:.2f}%"
        ],
        [
            "Fail",
            fail_count,
            f"{fail_percentage:.2f}%"
        ]
    ]

    verdict_table = Table(
        verdict_data,
        colWidths=[
            2.8 * inch,
            1.5 * inch,
            2.2 * inch
        ]
    )

    verdict_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#334155")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CBD5E1")
            ),
            (
                "ALIGN",
                (1, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(verdict_table)

    # =====================================================
    # IMPROVEMENT RECOMMENDATIONS
    # =====================================================

    story.append(
        Paragraph(
            "8. Improvement Recommendations",
            section_style
        )
    )

    recommendations = create_recommendations(summary)

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        story.append(
            Paragraph(
                f"{index}. {recommendation}",
                normal_style
            )
        )

        story.append(Spacer(1, 6))

    # =====================================================
    # FOOTER
    # =====================================================

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated by AI Response Validation System",
            subtitle_style
        )
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(story)

    buffer.seek(0)

    filename = "AI_Response_Validation_Report.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        }
    )


# =========================================================
# EXPORT EVALUATION REPORT
# =========================================================

@router.get("/export")
async def export_evaluation_report(
    evaluation_mode: Optional[str] = None,
    model: Optional[str] = None,
    dataset: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):

    evaluations = get_dashboard_evaluations(
        evaluation_mode=evaluation_mode,
        model=model,
        dataset=dataset,
        date_from=date_from,
        date_to=date_to
    )

    report_path = generate_evaluation_report(
        evaluations
    )

    return FileResponse(
        path=str(report_path),
        media_type="application/pdf",
        filename=report_path.name
    )