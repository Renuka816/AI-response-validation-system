# Mentor Demonstration & Walkthrough Guide

**Project Title**: AI Response Validation System  
**Full Title**: Development of AI Response Validation System with Hallucination Detection Assistance (Group 1)  
**Milestone**: Milestone 4 — Deliverable 7  
**Author**: Renuka Meesala  
**Date**: August 13, 2026  

---

## 🎯 Demonstration Objective

This guide outlines the step-by-step presentation script to demonstrate the platform to your mentor. You will showcase single evaluation, batch CSV upload, live analytics dashboard updates, PDF report export, and a live comparative evaluation between **two distinct AI systems**.

---

## 📋 Step-by-Step Demonstration Script

### Step 1: Project Introduction & Architecture (1 Minute)
- **Script**: *"Good morning/afternoon mentor. Today I am presenting the AI Response Quality Evaluator. Our platform uses RAG vector retrieval and 4 specialized evaluation agents—Accuracy, Hallucination, Relevance, and Completeness—to evaluate AI model responses objectively."*

### Step 2: Live Single Evaluation (2 Minutes)
1. Open the web interface at `http://localhost:5173`.
2. Enter a sample question:
   - **Question**: *"What causes malaria?"*
   - **AI Response**: *"Malaria is caused by Plasmodium parasites transmitted through female Anopheles mosquito bites."*
   - **AI Model**: `GPT-4o`
3. Click **"Evaluate AI Response"**.
4. Point out the agent score cards:
   - 🎯 **Accuracy Agent** (95%)
   - 🔗 **Relevance Agent** (95%)
   - ⚠️ **Hallucination Agent** (0% Detected / 100% Score)
   - 📋 **Completeness Agent** (90%)
   - 🏆 **Final Verdict**: `94.25% - Excellent`

---

### Step 3: Batch Evaluation & System A vs System B Comparison (3 Minutes)
1. Click **"📂 Batch Evaluation"**.
2. **Upload System A (High-Quality Model)**:
   - Select file [`datasets/ai_system_a_gpt4o.csv`](file:///c:/Users/hi/OneDrive/Desktop/AI_Response_Quality_Evaluator/datasets/ai_system_a_gpt4o.csv).
   - Click **"Evaluate Batch"**.
   - Show the summary: 5 records evaluated, Average Score ~95.1%, 0 Hallucinations.
3. **Upload System B (Flawed/Hallucinated Model)**:
   - Select file [`datasets/ai_system_b_llama.csv`](file:///c:/Users/hi/OneDrive/Desktop/AI_Response_Quality_Evaluator/datasets/ai_system_b_llama.csv).
   - Click **"Evaluate Batch"**.
   - Show the summary: 5 records evaluated, Average Score ~28.4%, 5 Hallucinations detected!

---

### Step 4: Analytics Dashboard & Filtering (2 Minutes)
1. Click **"📊 Evaluation Dashboard"**.
2. Point out:
   - Total Evaluations counter updated.
   - Grade Distribution pie chart (showing `Excellent` vs `Fail`).
   - Quality trend line chart over time.
3. **Filter by Model**:
   - Select `GPT-4o (System A)` in the Model filter dropdown $\rightarrow$ Shows 100% Pass rate.
   - Select `Llama-3-Base (System B)` in the Model filter dropdown $\rightarrow$ Shows 100% Fail / Hallucinated rate.

---

### Step 5: Export & Download PDF Executive Report (1 Minute)
1. Click **"📥 Export PDF Report"** button at the top right of the dashboard.
2. Open the downloaded PDF report and show your mentor:
   - Executive header and summary metrics.
   - Dimension-wise score breakdown.
   - Flagged hallucination list highlighting System B's incorrect claims.
   - Actionable improvement recommendations.

---

## 🏆 Key Summary Talking Points for Mentor

- **RAG Grounding**: Prevents generic evaluations by using ChromaDB document retrieval to check true facts.
- **Repeatable & Consistent**: Test suites prove $\sigma = 0.00$ variance across runs.
- **Enterprise-Ready**: Generates downloadable PDF reports for stakeholders.
