import API from "../services/api";

import { useState } from "react";

import Header from "../components/Header";

export default function BatchEvaluator({
  goBack,
  goToDashboard
}) {
  const [file, setFile] = useState(null);


const [results, setResults] = useState(null);

const [expandedCard, setExpandedCard] = useState(null);

  const handleUpload = async () => {

    if (!file) {
        alert("Please choose a CSV file.");
        return;
    }

    try {

        const formData = new FormData();
        formData.append("file", file);

        const response = await API.post(
            "/batch-evaluate",
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );

        console.log(response.data);

        setResults(response.data);

    } catch (error) {

        console.error(error);
        alert("Batch Evaluation Failed.");

    }
  };

  const downloadPDFReport = async () => {
    try {
      const response = await API.get("/dashboard/report/pdf", {
        params: { evaluation_mode: "batch" },
        responseType: "blob"
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "Batch_Evaluation_Report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to download PDF report.");
    }
  };

  return (
    <div className="app">

      <Header />

      <div className="glass-container">

        {/* Back Button */}
        <button
          onClick={goBack}
          style={{
            background: "none",
            border: "none",
            color: "#8b5cf6",
            cursor: "pointer",
            fontWeight: "600",
            fontSize: "15px",
            marginBottom: "30px",
          }}
        >
          ← Back to Single Evaluation
        </button>

        <button
  onClick={goToDashboard}
  style={{
    background: "none",
    border: "none",
    color: "#8b5cf6",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "15px",
    marginBottom: "30px",
    marginLeft: "20px"
  }}
>
  📊 Dashboard →
</button>

        {/* Page Content */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            padding: "20px",
          }}
        >

          <h1
            style={{
              color: "#ffffff",
              marginBottom: "12px",
              fontSize: "34px",
              fontWeight: "700",
            }}
          >
            📂 Batch Evaluation
          </h1>

          <p
            style={{
              color: "#cbd5e1",
              marginBottom: "30px",
              fontSize: "16px",
            }}
          >
            Upload a CSV containing multiple Question and AI Response pairs.
          </p>

          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
          />

          {file && (
            <p
              style={{
                marginTop: "15px",
                color: "#22c55e",
                fontWeight: "600",
              }}
            >
              Selected File: {file.name}
            </p>
          )}

          <button
            className="gradient-button"
            onClick={handleUpload}
            style={{
              marginTop: "30px",
              width: "260px",
            }}
          >
            Start Batch Evaluation
          </button>

          {results && (

<div style={{ width: "100%", marginTop: "45px" }}>

  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px", flexWrap: "wrap", gap: "15px" }}>
    <h2
      style={{
        color: "#fff",
        fontSize: "28px",
        fontWeight: "700",
        margin: 0
      }}
    >
      📊 Batch Evaluation Summary
    </h2>

    <button
      onClick={downloadPDFReport}
      style={{
        padding: "12px 24px",
        borderRadius: "12px",
        border: "none",
        background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        color: "white",
        fontWeight: "600",
        fontSize: "15px",
        cursor: "pointer",
        boxShadow: "0 4px 14px rgba(16, 185, 129, 0.4)",
        transition: "0.3s"
      }}
    >
      📥 Export Batch PDF Report
    </button>
  </div>

  {/* Summary Cards */}

  <div
    style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))",
      gap: "20px",
      marginBottom: "40px",
    }}
  >

    <div className="summary-card">
      <h4>Total Records</h4>
      <h2>{results.total_records}</h2>
    </div>

    <div className="summary-card">
      <h4>Average Score</h4>
      <h2>{results.average_score}</h2>
    </div>

    <div className="summary-card">
      <h4>Highest Score</h4>
      <h2>
        {Math.max(...results.results.map(r => r.final_score))}
      </h2>
    </div>

    <div className="summary-card">
      <h4>Lowest Score</h4>
      <h2>
        {Math.min(...results.results.map(r => r.final_score))}
      </h2>
    </div>

  </div>

  <h2
    style={{
      color: "white",
      marginBottom: "25px",
      textAlign: "center",
    }}
  >
    Individual Evaluations
  </h2>

  {results.results.map((item, index) => (

   <div
    key={index}
    className="glass-card"
    style={{
        marginBottom: "20px",
        padding: "25px",
    }}
>

<h3 style={{color:"white"}}>

❓ {item.question.length>70
? item.question.substring(0,70)+"..."
: item.question}

</h3>

<div
style={{
display:"flex",
justifyContent:"space-between",
alignItems:"center",
marginTop:"20px"
}}
>

<div>

<h2
style={{
color:"#4f8cff",
margin:0
}}
>

{item.final_score}/100

</h2>

<p style={{color:"#94a3b8"}}>

Final Score

</p>

</div>

<div>

<span
style={{
background:
item.grade==="Excellent"
?"#16a34a"
:item.grade==="Good"
?"#2563eb"
:item.grade==="Average"
?"#d97706"
:"#dc2626",

padding:"8px 18px",
borderRadius:"20px",
color:"white",
fontWeight:"600"
}}
>

{item.grade}

</span>

</div>

</div>

<button
className="gradient-button"
style={{
marginTop:"20px",
width:"220px"
}}
onClick={()=>

setExpandedCard(
expandedCard===index
?null
:index
)

}

>

{expandedCard===index

?"Hide Details ▲"

:"View Details ▼"}

</button>

{
expandedCard===index &&

<div
style={{
marginTop:"25px"
}}
>

<div
style={{
display:"grid",
gridTemplateColumns:"repeat(4,1fr)",
gap:"15px"
}}
>

<div className="mini-score">

  <span>Accuracy</span>

  <h3>{item.accuracy_score}</h3>

</div>

<div className="mini-score">

<span>Relevance</span>

<h3>{item.relevance_score}</h3>

</div>

<div className="mini-score">

<span>Hallucination</span>

<h3>{item.hallucination_score}</h3>

</div>

<div className="mini-score">

<span>Completeness</span>

<h3>{item.completeness_score}</h3>

</div>

</div>

<div
style={{
marginTop:"25px",
background:"#1f2937",
padding:"18px",
borderRadius:"12px",
color:"#cbd5e1"
}}
>

<strong
style={{
color:"white"
}}
>

Reason

</strong>

<br/><br/>

{item.reason}

</div>

</div>

}

</div>
  ))}

</div>

)}

        </div>

      </div>

    </div>
  );
}