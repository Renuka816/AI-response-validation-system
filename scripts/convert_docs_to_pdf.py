import os
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, Image as RLImage

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc = SimpleDocTemplate(
        str(pdf_path),
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
        "PDFTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=15,
        alignment=0
    )

    h1_style = ParagraphStyle(
        "PDFH1",
        parent=styles["Heading1"],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=8,
    )

    h2_style = ParagraphStyle(
        "PDFH2",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#334155"),
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "PDFBody",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    code_style = ParagraphStyle(
        "PDFCode",
        parent=styles["Code"],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=6,
    )

    story = []
    lines = content.split("\n")
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    def clean_text(text):
        # Escape xml entities for ReportLab Paragraph
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Bold markdown **text**
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        # Inline code `text`
        text = re.sub(r"`(.*?)`", r"<font face='Courier' color='#2563eb'>\1</font>", text)
        return text

    def flush_table(rows):
        if not rows:
            return
        parsed_table = []
        for r in rows:
            cols = [clean_text(c.strip()) for c in r.split("|")[1:-1]]
            parsed_table.append([Paragraph(c, body_style) for c in cols])
        
        if parsed_table:
            col_count = len(parsed_table[0])
            col_width = (A4[0] - 80) / max(col_count, 1)
            t = Table(parsed_table, colWidths=[col_width] * col_count)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))

    for line in lines:
        stripped = line.strip()

        # Handle Code Blocks ```
        if stripped.startswith("```"):
            if in_code_block:
                code_text = "\n".join(code_lines)
                story.append(Paragraph(clean_text(code_text), code_style))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Handle Tables
        if stripped.startswith("|"):
            if "---" in stripped:
                continue
            table_rows.append(stripped)
            in_table = True
            continue
        else:
            if in_table:
                flush_table(table_rows)
                table_rows = []
                in_table = False

        # Handle Images ![caption](path)
        img_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", stripped)
        if img_match:
            caption, img_rel_path = img_match.groups()
            resolved_img = (md_path.parent / img_rel_path).resolve()
            if not resolved_img.exists():
                resolved_img = (BASE_DIR / img_rel_path).resolve()
            if resolved_img.exists():
                try:
                    img_flowable = RLImage(str(resolved_img), width=6.5 * inch, height=3.6 * inch)
                    story.append(Spacer(1, 8))
                    story.append(img_flowable)
                    if caption:
                        caption_style = ParagraphStyle(
                            "PDFCaption",
                            parent=styles["Normal"],
                            fontSize=8.5,
                            leading=11,
                            textColor=colors.HexColor("#64748b"),
                            alignment=1,
                            spaceBefore=4,
                            spaceAfter=8,
                        )
                        story.append(Paragraph(clean_text(caption), caption_style))
                    else:
                        story.append(Spacer(1, 8))
                except Exception as img_err:
                    print(f"Warning embedding image {resolved_img}: {img_err}")
            continue

        # Handle Headings
        if stripped.startswith("# "):
            story.append(Paragraph(clean_text(stripped[2:]), title_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        elif stripped.startswith("## "):
            story.append(Paragraph(clean_text(stripped[3:]), h1_style))
        elif stripped.startswith("### "):
            story.append(Paragraph(clean_text(stripped[4:]), h2_style))
        elif stripped.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceBefore=6, spaceAfter=6))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            story.append(Paragraph(f"* {clean_text(stripped[2:])}", body_style))
        elif stripped:
            story.append(Paragraph(clean_text(stripped), body_style))

    if in_table:
        flush_table(table_rows)

    doc.build(story)
    print(f"[SUCCESS] Generated PDF: {pdf_path}")

def main():
    md_files = [f for f in DOCS_DIR.glob("*.md")]
    md_files.append(BASE_DIR / "README.md")

    print(f"Converting {len(md_files)} documentation files to PDF...")
    for md_file in md_files:
        if md_file.exists():
            pdf_file = md_file.with_suffix(".pdf")
            try:
                convert_md_to_pdf(md_file, pdf_file)
            except Exception as e:
                print(f"[ERROR] Failed to convert {md_file.name}: {e}")

if __name__ == "__main__":
    main()
