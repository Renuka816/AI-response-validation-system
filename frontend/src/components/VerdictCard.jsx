export default function VerdictCard({
  score,
  grade,
  confidence,
  recommendation,
}) {

  return (

    <div className="verdict-card">

      <h2>🏆 Final Verdict</h2>

      <div className="verdict-grid">

        <div>

          <small>Overall Score</small>

          <h1>{score}</h1>

        </div>

        <div>

          <small>Grade</small>

          <h1>{grade}</h1>

        </div>

        <div>

          <small>Confidence</small>

          <h1>{confidence}</h1>

        </div>

      </div>

      <div className="recommendation">

        <h3>Recommendation</h3>

        <p>{recommendation}</p>

      </div>

    </div>

  );

}