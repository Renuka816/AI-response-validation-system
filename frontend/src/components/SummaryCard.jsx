export default function SummaryCard({
  icon,
  title,
  value,
  color,
}) {
  return (
    <div className="summary-card">
      <div className="summary-icon">{icon}</div>

      <h3>{title}</h3>

      <h1 style={{ color }}>{value}</h1>
    </div>
  );
}