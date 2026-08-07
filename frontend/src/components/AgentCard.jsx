import ProgressBar from "./ProgressBar";

export default function AgentCard({
  icon,
  title,
  score,
  confidence,
  reason,
  children,
}) {

  const getColor = (value) => {
    if (value >= 80) return "#10B981";
    if (value >= 60) return "#3B82F6";
    if (value >= 40) return "#F59E0B";
    return "#EF4444";
  };

  return (
    <div className="agent-card">

      <div className="agent-header">

        <div className="agent-icon">{icon}</div>

        <div>
          <h3>{title}</h3>
          {confidence && (
            <span className="confidence-badge">
              {confidence}
            </span>
          )}
        </div>

      </div>

      <div className="score-area">

        <div
          className="score-circle"
          style={{ color: getColor(score) }}
        >
          {score?.toFixed(1)}
        </div>

        <ProgressBar value={score} />

      </div>

      {children}

      <div className="reason-box">

        <h4>Reason</h4>

        <p>{reason}</p>

      </div>

    </div>
  );
}