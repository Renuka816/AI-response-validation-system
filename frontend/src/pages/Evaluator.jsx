import { useState } from "react";


import Header from "../components/Header";
import InputCard from "../components/InputCard";
import GradientButton from "../components/GradientButton";
import API from "../services/api";
import SummaryCard from "../components/SummaryCard";
import AgentCard from "../components/AgentCard";
import VerdictCard from "../components/VerdictCard";

export default function Evaluator({ goToBatch }) {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const evaluateResponse = async () => {
    if (!question.trim() || !response.trim()) {
      alert("Please enter both Question and AI Response.");
      return;
    }

    setLoading(true);

   try {
  const res = await API.post("/evaluate", {
  question,
  response,
  reference_answer: "",
  source_document: "",
});

  console.log("API Response:", res.data.data);

  setResult(res.data.data);

} catch (error) {
      console.error(error);
      alert("Backend connection failed.");
    }

    setLoading(false);
  };

  const handleCSVUpload = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    console.log(file);

    alert("CSV selected. Batch Evaluation API will be connected next.");
};




const accuracy = result?.accuracy || {};
const relevance = result?.relevance || {};
const hallucination = result?.hallucination || {};
const completeness = result?.completeness || {};
const finalResult = result?.final_result || {};
console.log("Current Result:", result);
  return (
    <div className="app">

      <Header />

      <div className="glass-container">

        <InputCard
          title="Question"
          icon="❓"
          placeholder="Ask your question..."
          value={question}
          onChange={setQuestion}
          maxLength={500}
        />

        <InputCard
          title="AI Response"
          icon="💬"
          placeholder="Paste AI response here..."
          value={response}
          onChange={setResponse}
          maxLength={2000}
        />

      


       <GradientButton
  loading={loading}
  onClick={evaluateResponse}
/>

<div
  style={{
    marginTop: "24px",
    textAlign: "center",
    color: "#cbd5e1",
    fontSize: "15px",
  }}
>
  Want to evaluate multiple AI responses at once?
</div>

<button
  onClick={goToBatch}
  style={{
    width: "100%",
    marginTop: "12px",
    padding: "14px",
    border: "none",
    borderRadius: "12px",
    background: "#2f3547",
    color: "white",
    fontWeight: "600",
    fontSize: "16px",
    cursor: "pointer",
    transition: "0.3s",
  }}
  onMouseOver={(e) =>
    (e.target.style.background =
      "linear-gradient(90deg,#3563e9,#7c3aed)")
  }
  onMouseOut={(e) =>
    (e.target.style.background = "#2f3547")
  }
>
  📂 Batch Evaluation →
</button>


      </div>

            {result && (
  <div className="dashboard">

    <h2 className="dashboard-title">Evaluation Dashboard</h2>

    

    <div className="agent-grid">
<AgentCard
  icon="🎯"
  title="Accuracy Agent"
  score={result?.knowledge?.knowledge_score}
  confidence={result?.knowledge?.confidence}
  reason={result?.knowledge?.reason}
/>

      <AgentCard
        icon="🔗"
        title="Relevance Agent"
        score={result?.relevance?.relevance_score}
        confidence={result?.relevance?.confidence}
        reason={result?.relevance?.reason}
      >

        <p>
          <strong>Semantic Similarity:</strong>{" "}
          {result?.relevance?.semantic_similarity}
        </p>

        <p>
          <strong>Keyword Coverage:</strong>{" "}
          {result?.relevance?.keyword_coverage}
        </p>

        <p>
          <strong>Context Alignment:</strong>{" "}
          {result?.relevance?.context_alignment}
        </p>

      </AgentCard>

      <AgentCard
        icon="⚠"
        title="Hallucination Agent"
        score={result?.hallucination?.hallucination_score}
        reason={result?.hallucination?.reason}
        
      >

        <p>
          <strong>Status:</strong>{" "}
          {result?.hallucination?.hallucinated
            ? "❌ Detected"
            : "✅ None"}
        </p>



      </AgentCard>

      <AgentCard
        icon="📋"
        title="Completeness Agent"
        score={result?.completeness?.completeness_score}
        reason={result?.completeness?.reason}
      >

        <p>
          <strong>Coverage:</strong>{" "}
          {result?.completeness?.coverage}
        </p>

      </AgentCard>

    </div>

    <VerdictCard
      score={result?.final_result?.final_score}
      grade={result?.final_result?.grade}
      confidence={result?.relevance?.confidence}
      recommendation={result?.final_result?.reason}
    />

  </div>
)}
</div>
);
}