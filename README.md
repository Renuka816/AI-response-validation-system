# AI Response Validation System 🎯

**Full Project Title**: Development of AI Response Validation System with Hallucination Detection Assistance (Group 1)  
**Short Name**: AI Response Validation System  
**Author**: Renuka Meesala  

A production-grade, multi-agent evaluation platform for assessing generative AI model responses using RAG evidence retrieval, automated metric scoring, real-time analytics dashboard, and executive PDF report exports.

---

## 🌟 Key Features

- **Multi-Agent Evaluation Framework**: Evaluates responses across **Accuracy**, **Hallucination**, **Relevance**, and **Completeness**.
- **RAG-Powered Evidence Grounding**: Vector retrieval via **ChromaDB** checks facts against authentic knowledge sources.
- **Batch Evaluation Pipeline**: Upload CSV files containing bulk prompt-response datasets for automated evaluation.
- **Interactive Analytics Dashboard**: Real-time pass/fail rates, dimension averages, quality trends, and multi-filter criteria.
- **Executive PDF & HTML Export**: Programmatic report generation built with ReportLab featuring charts, flagged hallucination analysis, and recommendations.
- **Multi-Model Benchmark Comparison**: Evaluate and compare System A vs System B performance side-by-side.

---

## 📂 Project Structure

![Project Folder Structure Graphic](docs/images/folder_structure.png)

---

## 🚀 Quick Start

### 1. Start Backend Server
```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn backend.app:app --reload --port 8000
```

### 2. Start Frontend Web App
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🧪 Running Unit & E2E Tests

```bash
# Run End-to-End Test Suite
python -m unittest backend/tests/test_e2e_suite.py

# Run Scoring Consistency Validation
python -m unittest backend/tests/test_scoring_consistency.py
```

---

## 📄 Documentation Links

- 📖 [Technical Documentation](file:///c:/Users/hi/OneDrive/Desktop/AI_Response_Quality_Evaluator/docs/TECHNICAL_DOCUMENTATION.md)
- 📝 [Formal Project Report](file:///c:/Users/hi/OneDrive/Desktop/AI_Response_Quality_Evaluator/docs/PROJECT_REPORT.md)
- 🧪 [End-to-End Testing Report](file:///c:/Users/hi/OneDrive/Desktop/AI_Response_Quality_Evaluator/docs/E2E_TESTING_REPORT.md)
- 📊 [Scoring Consistency Report](file:///c:/Users/hi/OneDrive/Desktop/AI_Response_Quality_Evaluator/docs/SCORING_CONSISTENCY_REPORT.md)
- 🎤 [Mentor Demonstration Guide](file:///c:/Users/hi/OneDrive/Desktop/AI_Response_Quality_Evaluator/docs/DEMONSTRATION_GUIDE.md)
