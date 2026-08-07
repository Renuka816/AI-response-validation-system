import "../styles/Header.css";

export default function Header() {
  return (
    <header className="header">

      <div className="logo">

        <div className="logo-circle">
          🤖
        </div>

        <span>AI Evaluator</span>

      </div>

      <div className="title-section">

        <h1>AI Response Quality Evaluator</h1>

        <p>
          Evaluate AI-generated responses using
          RAG-based Multi-Agent Evaluation.
        </p>

      </div>

      <div className="status">

        <span className="green-dot"></span>

        Multi-Agent RAG

      </div>

    </header>
  );
}