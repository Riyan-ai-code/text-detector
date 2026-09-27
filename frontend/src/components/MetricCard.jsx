const MetricCard = ({ title, value, subtitle }) => {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      <span style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
        {title}
      </span>
      <h2 style={{ fontSize: "24px", fontWeight: "800", color: "var(--text-primary)", margin: "4px 0" }}>{value}</h2>
      <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{subtitle}</p>
    </div>
  );
};

export default MetricCard;