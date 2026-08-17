from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from pathlib import Path
from datetime import datetime


def generate_evaluation_report(evaluations):
    """
    Generate a structured PDF report for batch/single evaluations.

    Includes:
    - Project details
    - Batch summary
    - Result distribution
    - Dimension-wise score chart
    - Individual evaluation results
    - Grouped hallucinated responses
    - Overall verdict
    - Improvement recommendations

    Returns:
        Path: generated PDF file path
    """

    # =========================================================
    # REPORT LOCATION
    # =========================================================

    base_dir = Path(__file__).resolve().parent.parent.parent

    reports_dir = base_dir / "backend" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = (
        reports_dir
        / f"AI_Response_Validation_Report_{timestamp}.pdf"
    )

    # =========================================================
    # DOCUMENT
    # =========================================================

    document = SimpleDocTemplate(
        str(report_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        author="Renuka Meesala",
        creator="Renuka Meesala",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=15,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor("#1e293b"),
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    )

    story = []

    # =========================================================
    # HELPER FUNCTIONS
    # =========================================================

    def number(value):
        try:
            return round(float(value or 0), 2)
        except (ValueError, TypeError):
            return 0

    def paragraph(text, style=normal_style):
        text = str(text or "")

        text = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        return Paragraph(text, style)

    # =========================================================
    # EMPTY REPORT
    # =========================================================

    if not evaluations:

        story.append(
            Paragraph(
                "AI Response Validation System",
                title_style
            )
        )

        story.append(
            Paragraph(
                "No evaluation results were available.",
                subtitle_style
            )
        )

        document.build(story)

        return report_path

    # =========================================================
    # SUMMARY CALCULATIONS
    # =========================================================

    total = len(evaluations)

    pass_count = sum(
        1
        for item in evaluations
        if item.get("grade") == "Good"
    )

    needs_improvement_count = sum(
        1
        for item in evaluations
        if item.get("grade") == "Average"
    )

    fail_count = sum(
        1
        for item in evaluations
        if item.get("grade") == "Poor"
    )

    average_score = (
        sum(
            number(item.get("final_score"))
            for item in evaluations
        ) / total
    )

    average_accuracy = (
        sum(
            number(item.get("accuracy_score"))
            for item in evaluations
        ) / total
    )

    average_relevance = (
        sum(
            number(item.get("relevance_score"))
            for item in evaluations
        ) / total
    )

    average_completeness = (
        sum(
            number(item.get("completeness_score"))
            for item in evaluations
        ) / total
    )

    average_hallucination = (
        sum(
            number(item.get("hallucination_score"))
            for item in evaluations
        ) / total
    )

    hallucinated = [
        item
        for item in evaluations
        if item.get("hallucination_detected") == 1
        or number(item.get("hallucination_score")) < 50
    ]

    # =========================================================
    # PROJECT DETAILS
    # =========================================================

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
            "1. Project Details",
            heading_style
        )
    )

    project_data = [
        ["Project", "AI Response Validation System"],
        ["Full Title", "Development of AI Response Validation System with Hallucination Detection Assistance (Group 1)"],
        ["Author", "Renuka Meesala"],
        [
            "Evaluation Architecture",
            "Multi-Agent Evaluation + RAG"
        ],
        [
            "Evaluation Dimensions",
            "Accuracy, Relevance, Completeness, Hallucination"
        ],
        [
            "Evaluation Type",
            "Single / Batch"
        ],
        [
            "Report Generated",
            datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        ],
    ]

    project_table = Table(
        project_data,
        colWidths=[2.1 * inch, 4.4 * inch]
    )

    project_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#e8eefc")
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),
                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ]
        )
    )

    story.append(project_table)
    story.append(Spacer(1, 15))

    # =========================================================
    # BATCH SUMMARY
    # =========================================================

    story.append(
        Paragraph(
            "2. Batch Evaluation Summary",
            heading_style
        )
    )

    summary_data = [
        ["Metric", "Result"],
        ["Total Evaluations", total],
        ["Pass", pass_count],
        ["Needs Improvement", needs_improvement_count],
        ["Fail", fail_count],
        ["Average Score", f"{number(average_score)}/100"],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3.8 * inch, 2.7 * inch]
    )

    summary_table.setStyle(
        TableStyle(
            [
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
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#f8fafc")
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 20))

    # =========================================================
    # RESULT DISTRIBUTION CHART
    # =========================================================

    story.append(
        Paragraph(
            "3. Evaluation Result Distribution",
            heading_style
        )
    )

    result_chart = Drawing(430, 250)

    pie = Pie()

    pie.x = 100
    pie.y = 35
    pie.width = 170
    pie.height = 170

    pie.data = [
        pass_count,
        needs_improvement_count,
        fail_count
    ]

    pie.labels = [
        f"Pass ({pass_count})",
        f"Needs Improvement ({needs_improvement_count})",
        f"Fail ({fail_count})"
    ]

    pie.slices.strokeWidth = 1

    pie.slices[0].fillColor = colors.HexColor("#22c55e")
    pie.slices[1].fillColor = colors.HexColor("#f59e0b")
    pie.slices[2].fillColor = colors.HexColor("#ef4444")

    result_chart.add(pie)

    story.append(result_chart)

    story.append(Spacer(1, 10))

    # =========================================================
    # DIMENSION-WISE SCORES
    # =========================================================

    story.append(
        Paragraph(
            "4. Dimension-wise Evaluation Scores",
            heading_style
        )
    )

    dimension_data = [
        ["Dimension", "Average Score"],
        [
            "Accuracy",
            f"{number(average_accuracy)}/100"
        ],
        [
            "Relevance",
            f"{number(average_relevance)}/100"
        ],
        [
            "Completeness",
            f"{number(average_completeness)}/100"
        ],
        [
            "Hallucination Score",
            f"{number(average_hallucination)}/100"
        ],
    ]

    dimension_table = Table(
        dimension_data,
        colWidths=[3.8 * inch, 2.7 * inch]
    )

    dimension_table.setStyle(
        TableStyle(
            [
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
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ]
        )
    )

    story.append(dimension_table)
    story.append(Spacer(1, 20))

    # =========================================================
    # DIMENSION SCORE BAR CHART
    # =========================================================

    story.append(
        Paragraph(
            "Dimension Score Comparison",
            ParagraphStyle(
                "ChartHeading",
                parent=styles["Heading3"],
                fontSize=12,
                spaceBefore=8,
                spaceAfter=8,
            )
        )
    )

    dimension_chart = Drawing(460, 280)

    bar_chart = VerticalBarChart()

    bar_chart.x = 55
    bar_chart.y = 55
    bar_chart.height = 180
    bar_chart.width = 350

    bar_chart.data = [[
        number(average_accuracy),
        number(average_relevance),
        number(average_completeness),
        number(average_hallucination)
    ]]

    bar_chart.categoryAxis.categoryNames = [
        "Accuracy",
        "Relevance",
        "Completeness",
        "Hallucination"
    ]

    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = 100
    bar_chart.valueAxis.valueStep = 20

    bar_chart.bars[0].fillColor = colors.HexColor("#4f8cff")

    bar_chart.categoryAxis.labels.fontSize = 8
    bar_chart.valueAxis.labels.fontSize = 8

    bar_chart.categoryAxis.labels.angle = 0

    dimension_chart.add(bar_chart)

    story.append(dimension_chart)

    # =========================================================
    # INDIVIDUAL RESULTS
    # =========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "5. Individual Evaluation Results",
            heading_style
        )
    )

    individual_data = [
        [
            "ID",
            "Question",
            "Accuracy",
            "Relevance",
            "Completeness",
            "Hallucination",
            "Final",
            "Verdict",
        ]
    ]

    for index, item in enumerate(evaluations, start=1):

        question = str(item.get("question", ""))

        if len(question) > 55:
            question = question[:52] + "..."

        individual_data.append(
            [
                str(item.get("id", index)),
                paragraph(question, small_style),
                number(item.get("accuracy_score")),
                number(item.get("relevance_score")),
                number(item.get("completeness_score")),
                number(item.get("hallucination_score")),
                number(item.get("final_score")),
                str(item.get("grade", "N/A")),
            ]
        )

    individual_table = Table(
        individual_data,
        colWidths=[
            0.35 * inch,
            2.15 * inch,
            0.65 * inch,
            0.65 * inch,
            0.75 * inch,
            0.75 * inch,
            0.55 * inch,
            0.75 * inch,
        ],
        repeatRows=1,
    )

    individual_table.setStyle(
        TableStyle(
            [
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
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
            ]
        )
    )

    story.append(individual_table)

    # =========================================================
    # GROUP HALLUCINATED RESPONSES
    # =========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "6. Hallucinated Responses",
            heading_style
        )
    )

    if not hallucinated:

        story.append(
            paragraph(
                "No hallucinated responses were detected "
                "in the selected evaluations."
            )
        )

    else:

        # -----------------------------------------------------
        # Group by identical question
        # -----------------------------------------------------

        grouped_hallucinations = {}

        for item in hallucinated:

            question = str(
                item.get("question", "")
            ).strip()

            if question not in grouped_hallucinations:
                grouped_hallucinations[question] = []

            grouped_hallucinations[question].append(item)

        # -----------------------------------------------------
        # Display each unique question once
        # -----------------------------------------------------

        for index, (question, items) in enumerate(
            grouped_hallucinations.items(),
            start=1
        ):

            story.append(
                Paragraph(
                    f"Flagged Question {index}",
                    ParagraphStyle(
                        f"flag_heading_{index}",
                        parent=styles["Heading3"],
                        fontSize=11,
                        spaceBefore=8,
                        spaceAfter=5,
                    )
                )
            )

            story.append(
                paragraph(
                    f"<b>Question:</b> {question}"
                )
            )

            story.append(Spacer(1, 6))

            story.append(
                paragraph(
                    f"<b>Occurrences:</b> {len(items)}"
                )
            )

            story.append(Spacer(1, 6))

            # Show each unique response only once
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
                    paragraph(
                        f"<b>Response {response_index}:</b> "
                        f"{response}"
                    )
                )

                story.append(Spacer(1, 5))

            scores = [
                number(
                    item.get("hallucination_score")
                )
                for item in items
            ]

            average_hallucination_flagged = (
                sum(scores) / len(scores)
                if scores
                else 0
            )

            story.append(
                paragraph(
                    f"<b>Average Hallucination Score:</b> "
                    f"{number(average_hallucination_flagged)}/100"
                )
            )

            verdicts = set(
                str(item.get("grade", "N/A"))
                for item in items
            )

            story.append(
                paragraph(
                    f"<b>Verdict:</b> "
                    f"{', '.join(verdicts)}"
                )
            )

            story.append(Spacer(1, 15))

    # =========================================================
    # IMPROVEMENT RECOMMENDATIONS
    # =========================================================

    story.append(
        Paragraph(
            "7. Improvement Recommendations",
            heading_style
        )
    )

    recommendations = []

    if average_accuracy < 70:

        recommendations.append(
            "Improve factual accuracy by strengthening "
            "reference-based retrieval and validating generated "
            "answers against trusted sources."
        )

    if average_relevance < 70:

        recommendations.append(
            "Improve relevance by retrieving context that is more "
            "closely aligned with the user's question."
        )

    if average_completeness < 70:

        recommendations.append(
            "Improve completeness by ensuring that responses "
            "address all important aspects of the question."
        )

    if average_hallucination < 70 or hallucinated:

        recommendations.append(
            "Reduce hallucinations by improving retrieval grounding "
            "and using the hallucination evaluation agent to identify "
            "unsupported claims."
        )

    if fail_count > 0:

        recommendations.append(
            "Review failed evaluations individually and identify "
            "recurring patterns across accuracy, relevance, "
            "completeness, and hallucination."
        )

    if not recommendations:

        recommendations.append(
            "Overall evaluation quality is satisfactory. Continue "
            "monitoring evaluation trends and periodically review "
            "flagged responses."
        )

    for recommendation in recommendations:

        story.append(
            Paragraph(
                f"• {recommendation}",
                normal_style
            )
        )

        story.append(Spacer(1, 6))

    # =========================================================
    # OVERALL VERDICT
    # =========================================================

    story.append(
        Paragraph(
            "8. Overall Verdict",
            heading_style
        )
    )

    if average_score >= 80:

        overall_verdict = "Good"

    elif average_score >= 50:

        overall_verdict = "Average"

    else:

        overall_verdict = "Poor"

    story.append(
        paragraph(
            f"The evaluated responses achieved an average overall "
            f"score of {number(average_score)}/100. Based on the "
            f"configured evaluation thresholds, the overall batch "
            f"verdict is <b>{overall_verdict}</b>."
        )
    )

    # =========================================================
    # FOOTER
    # =========================================================

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "Generated by AI Response Validation System",
            subtitle_style
        )
    )

    # =========================================================
    # BUILD PDF
    # =========================================================

    document.build(story)

    return report_path