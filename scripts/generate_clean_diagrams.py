import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Helper function to get fonts
def get_font(size, is_bold=False):
    # Standard Windows fonts
    font_names = [
        "segoeui.ttf" if not is_bold else "segoeuib.ttf",
        "arial.ttf" if not is_bold else "arialbd.ttf",
        "calibri.ttf" if not is_bold else "calibrib.ttf",
    ]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, xy, corner_radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=corner_radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, start, end, color="#64748b", width=3, arrow_size=10):
    x1, y1 = start
    x2, y2 = end
    draw.line([x1, y1, x2, y2], fill=color, width=width)
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    # Draw arrow head
    px1 = x2 - arrow_size * math.cos(angle - math.pi / 6)
    py1 = y2 - arrow_size * math.sin(angle - math.pi / 6)
    px2 = x2 - arrow_size * math.cos(angle + math.pi / 6)
    py2 = y2 - arrow_size * math.sin(angle + math.pi / 6)
    draw.polygon([(x2, y2), (px1, py1), (px2, py2)], fill=color)

# 1. GENERATE SYSTEM ARCHITECTURE DIAGRAM
def generate_system_architecture():
    W, H = 1600, 1100
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    title_font = get_font(34, is_bold=True)
    subtitle_font = get_font(18, is_bold=False)
    box_title_font = get_font(20, is_bold=True)
    box_sub_font = get_font(15, is_bold=False)

    # Title Banner
    draw_rounded_rect(draw, (60, 40, W - 60, 130), 16, fill="#1E293B")
    draw.text((W // 2, 70), "AI RESPONSE QUALITY EVALUATOR", fill="#FFFFFF", font=title_font, anchor="mm")
    draw.text((W // 2, 105), "System Architecture Overview & Layer Interactions", fill="#94A3B8", font=subtitle_font, anchor="mm")

    # Define Cards/Boxes
    # Row 1: Frontend & Gateway & RAG
    # Left: Frontend UI
    draw_rounded_rect(draw, (80, 180, 480, 360), 12, fill="#EFF6FF", outline="#3B82F6", width=2)
    draw.text((280, 220), "Frontend Interface", fill="#1E3A8A", font=box_title_font, anchor="mm")
    draw.text((280, 260), "React Dashboard & Evaluation UI", fill="#3B82F6", font=box_sub_font, anchor="mm")
    draw.text((280, 295), "Batch CSV File Drag-and-Drop", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((280, 325), "Recharts Visualization Components", fill="#475569", font=box_sub_font, anchor="mm")

    # Middle: FastAPI Gateway
    draw_rounded_rect(draw, (580, 180, 1020, 360), 12, fill="#F0FDFA", outline="#0D9488", width=2)
    draw.text((800, 220), "FastAPI Backend Gateway", fill="#115E59", font=box_title_font, anchor="mm")
    draw.text((800, 260), "Endpoints: /api/evaluate | /api/batch-evaluate", fill="#0D9488", font=box_sub_font, anchor="mm")
    draw.text((800, 295), "Request Validation (Pydantic Schemas)", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((800, 325), "CORS Bridge & Dashboard Router", fill="#475569", font=box_sub_font, anchor="mm")

    # Right: RAG Vector Knowledge Engine
    draw_rounded_rect(draw, (1120, 180, 1520, 360), 12, fill="#FEF3C7", outline="#D97706", width=2)
    draw.text((1320, 220), "RAG Evidence Engine", fill="#92400E", font=box_title_font, anchor="mm")
    draw.text((1320, 260), "ChromaDB Vector Store", fill="#D97706", font=box_sub_font, anchor="mm")
    draw.text((1320, 295), "MiniLM-L6-v2 Semantic Embeddings", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((1320, 325), "Top-k Document Context Retrieval", fill="#475569", font=box_sub_font, anchor="mm")

    # Arrows between Row 1
    draw_arrow(draw, (480, 270), (575, 270), color="#3B82F6", width=3)
    draw_arrow(draw, (1020, 270), (1115, 270), color="#0D9488", width=3)

    # Row 2: Multi-Agent Evaluation Framework
    draw_rounded_rect(draw, (80, 430, W - 80, 780), 16, fill="#F8FAFC", outline="#64748B", width=2)
    draw.text((W // 2, 465), "Multi-Agent Evaluation Framework", fill="#0F172A", font=get_font(24, is_bold=True), anchor="mm")

    # 4 Agents Inside
    agent_width = 330
    agent_y1, agent_y2 = 510, 740

    # Agent 1: Accuracy
    draw_rounded_rect(draw, (110, agent_y1, 110 + agent_width, agent_y2), 12, fill="#FFFFFF", outline="#2563EB", width=2)
    draw.text((110 + agent_width//2, 545), "Accuracy Agent", fill="#1E40AF", font=box_title_font, anchor="mm")
    draw.text((110 + agent_width//2, 580), "Weight: 35%", fill="#2563EB", font=box_sub_font, anchor="mm")
    draw.text((110 + agent_width//2, 620), "• Factuality Verification", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((110 + agent_width//2, 650), "• Deterministic Logic Rules", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((110 + agent_width//2, 680), "• Reference Math Checking", fill="#475569", font=box_sub_font, anchor="mm")

    # Agent 2: Hallucination
    draw_rounded_rect(draw, (470, agent_y1, 470 + agent_width, agent_y2), 12, fill="#FFFFFF", outline="#DC2626", width=2)
    draw.text((470 + agent_width//2, 545), "Hallucination Agent", fill="#991B1B", font=box_title_font, anchor="mm")
    draw.text((470 + agent_width//2, 580), "Weight: 25%", fill="#DC2626", font=box_sub_font, anchor="mm")
    draw.text((470 + agent_width//2, 620), "• Semantic Distance Analysis", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((470 + agent_width//2, 650), "• Ungrounded Claim Detection", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((470 + agent_width//2, 680), "• RAG Evidence Alignment", fill="#475569", font=box_sub_font, anchor="mm")

    # Agent 3: Relevance
    draw_rounded_rect(draw, (830, agent_y1, 830 + agent_width, agent_y2), 12, fill="#FFFFFF", outline="#7C3AED", width=2)
    draw.text((830 + agent_width//2, 545), "Relevance Agent", fill="#5B21B6", font=box_title_font, anchor="mm")
    draw.text((830 + agent_width//2, 580), "Weight: 20%", fill="#7C3AED", font=box_sub_font, anchor="mm")
    draw.text((830 + agent_width//2, 620), "• Intent Alignment", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((830 + agent_width//2, 650), "• Prompt-Response Match", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((830 + agent_width//2, 680), "• Key Concept Coverage", fill="#475569", font=box_sub_font, anchor="mm")

    # Agent 4: Completeness
    draw_rounded_rect(draw, (1190, agent_y1, 1190 + agent_width, agent_y2), 12, fill="#FFFFFF", outline="#059669", width=2)
    draw.text((1190 + agent_width//2, 545), "Completeness Agent", fill="#065F46", font=box_title_font, anchor="mm")
    draw.text((1190 + agent_width//2, 580), "Weight: 20%", fill="#059669", font=box_sub_font, anchor="mm")
    draw.text((1190 + agent_width//2, 620), "• Sub-question Coverage", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((1190 + agent_width//2, 650), "• Depth & Detail Check", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((1190 + agent_width//2, 680), "• Entity Completeness", fill="#475569", font=box_sub_font, anchor="mm")

    # Arrows from Row 1 Gateway & RAG to Multi-Agent Box
    draw_arrow(draw, (800, 360), (800, 425), color="#0D9488", width=3)

    # Row 3: Composite Scoring & Output Storage
    # Composite Scoring Engine
    draw_rounded_rect(draw, (80, 850, 520, 1020), 12, fill="#F3E8FF", outline="#9333EA", width=2)
    draw.text((300, 890), "Composite Scoring Engine", fill="#6B21A8", font=box_title_font, anchor="mm")
    draw.text((300, 925), "Weighted Score: 0 - 100%", fill="#9333EA", font=box_sub_font, anchor="mm")
    draw.text((300, 960), "Grade: Excellent / Good / Avg / Poor", fill="#475569", font=box_sub_font, anchor="mm")

    # Storage & Persistence
    draw_rounded_rect(draw, (590, 850, 1010, 1020), 12, fill="#F1F5F9", outline="#475569", width=2)
    draw.text((800, 890), "SQLite Analytics DB", fill="#0F172A", font=box_title_font, anchor="mm")
    draw.text((800, 925), "evaluations.db Storage", fill="#475569", font=box_sub_font, anchor="mm")
    draw.text((800, 960), "Metrics & Historical Queries", fill="#475569", font=box_sub_font, anchor="mm")

    # Output Generators
    draw_rounded_rect(draw, (1080, 850, 1520, 1020), 12, fill="#ECFDF5", outline="#10B981", width=2)
    draw.text((1300, 890), "Output Presentation", fill="#065F46", font=box_title_font, anchor="mm")
    draw.text((1300, 925), "Recharts Interactive Web Dashboard", fill="#10B981", font=box_sub_font, anchor="mm")
    draw.text((1300, 960), "ReportLab PDF Executive Export", fill="#475569", font=box_sub_font, anchor="mm")

    # Arrows from Agents to Scoring to Outputs
    draw_arrow(draw, (800, 780), (300, 845), color="#64748B", width=3)
    draw_arrow(draw, (520, 935), (585, 935), color="#9333EA", width=3)
    draw_arrow(draw, (1010, 935), (1075, 935), color="#475569", width=3)

    img.save(IMAGES_DIR / "system_architecture.png")
    print(f"[SUCCESS] Saved system_architecture.png")

# 2. GENERATE SYSTEM DESIGN DIAGRAM
def generate_system_design():
    W, H = 1600, 900
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    title_font = get_font(32, is_bold=True)
    sub_font = get_font(17, is_bold=False)
    header_font = get_font(18, is_bold=True)
    body_font = get_font(14, is_bold=False)

    # Title
    draw.text((W // 2, 45), "AI RESPONSE QUALITY EVALUATION SYSTEM DESIGN", fill="#0F172A", font=title_font, anchor="mm")
    draw.text((W // 2, 80), "End-to-End Multi-Agent Data Processing Pipeline", fill="#64748B", font=sub_font, anchor="mm")

    # 5 Horizontal Stages
    stages = [
        {"title": "1. Input Data", "sub": "User Prompt &\nAI Response Pair", "color": "#2563EB", "fill": "#EFF6FF"},
        {"title": "2. RAG Retrieval", "sub": "ChromaDB Vector Store\n(MiniLM Embeddings)", "color": "#D97706", "fill": "#FEF3C7"},
        {"title": "3. Multi-Agent Eval", "sub": "4 Specialized Agents\n(Accuracy, Hallucination,\nRelevance, Completeness)", "color": "#7C3AED", "fill": "#F3E8FF"},
        {"title": "4. Scoring Engine", "sub": "Weighted Score (0-100%)\n& Grade Classifier", "color": "#059669", "fill": "#ECFDF5"},
        {"title": "5. Outputs", "sub": "SQLite Database,\nReact Dashboard &\nReportLab PDF Export", "color": "#0F172A", "fill": "#F1F5F9"},
    ]

    card_w = 260
    card_h = 240
    start_x = 70
    gap = 50
    card_y = 140

    for i, st in enumerate(stages):
        cx = start_x + i * (card_w + gap)
        draw_rounded_rect(draw, (cx, card_y, cx + card_w, card_y + card_h), 14, fill=st["fill"], outline=st["color"], width=2)
        draw.text((cx + card_w // 2, card_y + 35), st["title"], fill=st["color"], font=header_font, anchor="mm")
        
        lines = st["sub"].split("\n")
        ly = card_y + 90
        for l in lines:
            draw.text((cx + card_w // 2, ly), l, fill="#334155", font=body_font, anchor="mm")
            ly += 26

        if i < len(stages) - 1:
            arrow_start = (cx + card_w, card_y + card_h // 2)
            arrow_end = (cx + card_w + gap, card_y + card_h // 2)
            draw_arrow(draw, arrow_start, arrow_end, color="#64748B", width=3, arrow_size=10)

    # Detailed Agent Weights Breakdown Box below Stage 3
    draw_rounded_rect(draw, (70, 440, W - 70, 830), 16, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((W // 2, 475), "Detailed Multi-Agent Weighting & Evaluation Criteria", fill="#0F172A", font=get_font(22, is_bold=True), anchor="mm")

    agents_detail = [
        {"name": "Accuracy Agent", "weight": "35%", "desc": "Verifies factual correctness against retrieved RAG evidence passages and mathematical logic rules.", "color": "#2563EB"},
        {"name": "Hallucination Agent", "weight": "25%", "desc": "Calculates semantic distance to detect ungrounded claims or hallucinated facts not supported by evidence.", "color": "#DC2626"},
        {"name": "Relevance Agent", "weight": "20%", "desc": "Evaluates prompt-response intent alignment, semantic similarity, and key concept coverage.", "color": "#7C3AED"},
        {"name": "Completeness Agent", "weight": "20%", "desc": "Assesses sub-question coverage, depth of explanation, and required detail completeness.", "color": "#059669"},
    ]

    ay = 520
    for ag in agents_detail:
        draw_rounded_rect(draw, (100, ay, W - 100, ay + 65), 10, fill="#FFFFFF", outline=ag["color"], width=2)
        draw.text((130, ay + 32), ag["name"], fill=ag["color"], font=get_font(18, is_bold=True), anchor="lm")
        draw_rounded_rect(draw, (360, ay + 15, 450, ay + 50), 8, fill=ag["color"])
        draw.text((405, ay + 32), ag["weight"], fill="#FFFFFF", font=get_font(15, is_bold=True), anchor="mm")
        draw.text((480, ay + 32), ag["desc"], fill="#334155", font=get_font(15, is_bold=False), anchor="lm")
        ay += 75

    img.save(IMAGES_DIR / "system_design.png")
    print(f"[SUCCESS] Saved system_design.png")

# 3. GENERATE FOLDER STRUCTURE DIAGRAM
def generate_folder_structure():
    W, H = 1600, 1100
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    title_font = get_font(32, is_bold=True)
    sub_font = get_font(17, is_bold=False)
    folder_font = get_font(18, is_bold=True)
    file_font = get_font(14, is_bold=False)
    desc_font = get_font(13, is_bold=False)

    # Title Banner
    draw_rounded_rect(draw, (60, 40, W - 60, 120), 14, fill="#0F172A")
    draw.text((W // 2, 68), "PROJECT REPOSITORY STRUCTURE", fill="#FFFFFF", font=title_font, anchor="mm")
    draw.text((W // 2, 100), "AI Response Quality Evaluator — Directory & File Architecture", fill="#94A3B8", font=sub_font, anchor="mm")

    # 3 Columns for cleanly structured layout
    col_w = 460
    col_h = 900
    col_y = 150

    # Column 1: Backend Architecture
    cx1 = 60
    draw_rounded_rect(draw, (cx1, col_y, cx1 + col_w, col_y + col_h), 14, fill="#FFFFFF", outline="#3B82F6", width=2)
    draw_rounded_rect(draw, (cx1 + 15, col_y + 15, cx1 + col_w - 15, col_y + 60), 8, fill="#EFF6FF")
    draw.text((cx1 + 30, col_y + 37), "backend/", fill="#1E40AF", font=folder_font, anchor="lm")
    draw.text((cx1 + col_w - 30, col_y + 37), "Core API & Agents", fill="#3B82F6", font=desc_font, anchor="rm")

    backend_items = [
        ("app.py", "FastAPI app entry point & CORS config", False),
        ("database/", "SQLite database schema & query logic", True),
        ("  - database.py", "Database initialization & metrics", False),
        ("  - evaluations.db", "Persistent SQLite database storage", False),
        ("models/", "Pydantic request & response schemas", True),
        ("reports/", "Generated PDF & HTML reports storage", True),
        ("routes/", "API route handlers", True),
        ("  - evaluation.py", "/api/evaluate single endpoint", False),
        ("  - batch_evaluation.py", "/api/batch-evaluate CSV endpoint", False),
        ("  - dashboard.py", "/api/dashboard summary & exports", False),
        ("services/", "Multi-agent engines & PDF generator", True),
        ("  - accuracy_agent.py", "Factuality & reference checking", False),
        ("  - hallucination_agent.py", "Ungrounded claim detection", False),
        ("  - relevance_agent.py", "Semantic intent alignment", False),
        ("  - completeness_agent.py", "Depth & sub-question coverage", False),
        ("  - rag_service.py", "ChromaDB vector retrieval", False),
        ("  - scoring_service.py", "Weighted score computation", False),
        ("  - report_generator.py", "ReportLab PDF report builder", False),
        ("tests/", "Automated test suites", True),
        ("  - test_e2e_suite.py", "End-to-End system test suite", False),
        ("  - test_scoring_consistency.py", "Score repeatability validator", False),
    ]

    by = col_y + 80
    for name, desc, is_dir in backend_items:
        f_color = "#1E40AF" if is_dir else "#334155"
        f_font = get_font(15, is_bold=True) if is_dir else file_font
        prefix = "> " if is_dir else ""
        draw.text((cx1 + 25, by), prefix + name, fill=f_color, font=f_font, anchor="lm")
        draw.text((cx1 + col_w - 20, by), desc, fill="#64748B", font=desc_font, anchor="rm")
        by += 38

    # Column 2: Frontend & Docs
    cx2 = 570
    draw_rounded_rect(draw, (cx2, col_y, cx2 + col_w, col_y + col_h), 14, fill="#FFFFFF", outline="#7C3AED", width=2)
    draw_rounded_rect(draw, (cx2 + 15, col_y + 15, cx2 + col_w - 15, col_y + 60), 8, fill="#F3E8FF")
    draw.text((cx2 + 30, col_y + 37), "frontend/ & docs/", fill="#5B21B6", font=folder_font, anchor="lm")
    draw.text((cx2 + col_w - 30, col_y + 37), "UI & Documentation", fill="#7C3AED", font=desc_font, anchor="rm")

    frontend_docs_items = [
        ("frontend/", "Vite + React Web App", True),
        ("  - src/components/", "UI Cards & Progress bars", True),
        ("  - src/pages/", "Evaluator, Batch & Dashboard", True),
        ("  - src/services/", "Axios API connection bridge", True),
        ("  - package.json", "Node dependencies & scripts", False),
        ("docs/", "Project Documentation", True),
        ("  - images/", "Diagrams & visual assets", True),
        ("  - TECHNICAL_DOCUMENTATION.md", "Complete technical spec", False),
        ("  - PROJECT_REPORT.md", "Formal project report", False),
        ("  - E2E_TESTING_REPORT.md", "Verification test report", False),
        ("  - SCORING_CONSISTENCY_REPORT.md", "Repeatability report", False),
        ("  - DEMONSTRATION_GUIDE.md", "Mentor presentation guide", False),
        ("  - *.pdf", "Compiled PDF documents", False),
    ]

    fy = col_y + 80
    for name, desc, is_dir in frontend_docs_items:
        f_color = "#5B21B6" if is_dir else "#334155"
        f_font = get_font(15, is_bold=True) if is_dir else file_font
        prefix = "> " if is_dir else ""
        draw.text((cx2 + 25, fy), prefix + name, fill=f_color, font=f_font, anchor="lm")
        draw.text((cx2 + col_w - 20, fy), desc, fill="#64748B", font=desc_font, anchor="rm")
        fy += 42

    # Column 3: Datasets, Scripts & Environment
    cx3 = 1080
    draw_rounded_rect(draw, (cx3, col_y, cx3 + col_w, col_y + col_h), 14, fill="#FFFFFF", outline="#059669", width=2)
    draw_rounded_rect(draw, (cx3 + 15, col_y + 15, cx3 + col_w - 15, col_y + 60), 8, fill="#ECFDF5")
    draw.text((cx3 + 30, col_y + 37), "datasets/, scripts/ & Root", fill="#065F46", font=folder_font, anchor="lm")
    draw.text((cx3 + col_w - 30, col_y + 37), "Data & Config", fill="#059669", font=desc_font, anchor="rm")

    dataset_script_items = [
        ("datasets/", "Benchmark Datasets", True),
        ("  - ai_system_a_gpt4o.csv", "System A test dataset", False),
        ("  - ai_system_b_llama.csv", "System B test dataset", False),
        ("scripts/", "Automation Utilities", True),
        ("  - convert_docs_to_pdf.py", "MD to PDF converter", False),
        ("vector_store/", "ChromaDB vector collection", True),
        ("requirements.txt", "Python dependencies", False),
        ("README.md", "Project overview & setup", False),
        (".env", "Environment configuration", False),
    ]

    sy = col_y + 80
    for name, desc, is_dir in dataset_script_items:
        f_color = "#065F46" if is_dir else "#334155"
        f_font = get_font(15, is_bold=True) if is_dir else file_font
        prefix = "> " if is_dir else ""
        draw.text((cx3 + 25, sy), prefix + name, fill=f_color, font=f_font, anchor="lm")
        draw.text((cx3 + col_w - 20, sy), desc, fill="#64748B", font=desc_font, anchor="rm")
        sy += 45

    img.save(IMAGES_DIR / "folder_structure.png")
    print(f"[SUCCESS] Saved folder_structure.png")

if __name__ == "__main__":
    generate_system_architecture()
    generate_system_design()
    generate_folder_structure()
