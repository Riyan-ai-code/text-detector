import React from "react";
import { CheckCircle2, AlertCircle, Scale, Cpu, BarChart2, Zap } from "lucide-react";

const ModelConsensusMatrix = ({ consensus = {}, breakdown = {} }) => {
  if (!consensus || !consensus.model_votes) {
    return null;
  }

  const {
    status,
    verdict,
    badge,
    color,
    ai_votes,
    human_votes,
    total_models = 3,
    agreement_pct = 100,
    model_votes = []
  } = consensus;

  const getModelIcon = (id) => {
    switch (id) {
      case "model_1":
        return <Cpu size={18} color="#38bdf8" />;
      case "model_2":
        return <BarChart2 size={18} color="#818cf8" />;
      case "model_3":
        return <Zap size={18} color="#c084fc" />;
      default:
        return <Scale size={18} color="#3b82f6" />;
    }
  };

  const getModelDescription = (id) => {
    switch (id) {
      case "model_1":
        return "Deep contextual semantic attention (512-token max sequence)";
      case "model_2":
        return "Word N-gram statistical frequency with SGD regularization";
      case "model_3":
        return "Dual Word + Subword Char-WB Stacking Ensemble";
      default:
        return "";
    }
  };

  return (
    <div
      style={{
        background: "var(--bg-card)",
        padding: "20px",
        borderRadius: "12px",
        border: "1px solid var(--border-color)",
        marginTop: "24px"
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          marginBottom: "16px"
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "20px" }}>⚖️</span>
            <h3 style={{ margin: 0, fontSize: "17px", fontWeight: "700", color: "var(--text-primary)" }}>
              Multi-Model Consensus & Agreement Matrix
            </h3>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "var(--text-muted)" }}>
            Triangulated verification preventing single-model false positives through multi-architecture voting.
          </p>
        </div>

        {/* Consensus Badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            background: "var(--bg-inner)",
            padding: "6px 14px",
            borderRadius: "20px",
            border: `1.5px solid ${color || "#3b82f6"}`
          }}
        >
          {ai_votes === 3 || human_votes === 3 ? (
            <CheckCircle2 size={16} color={color} />
          ) : (
            <AlertCircle size={16} color={color} />
          )}
          <span style={{ fontSize: "13px", fontWeight: "700", color: color || "var(--text-primary)" }}>
            {verdict} ({badge})
          </span>
        </div>
      </div>

      {/* Model Voting Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "14px"
        }}
      >
        {model_votes.map((mv) => {
          const isAi = mv.vote === "AI";
          const confVal = mv.confidence !== null && mv.confidence !== undefined ? Math.round(mv.confidence * 100) : 50;

          return (
            <div
              key={mv.id}
              style={{
                background: "var(--bg-inner)",
                padding: "16px",
                borderRadius: "10px",
                border: `1px solid ${isAi ? "rgba(239, 68, 68, 0.4)" : "rgba(34, 197, 94, 0.4)"}`,
                display: "flex",
                flexDirection: "column",
                gap: "10px",
                position: "relative"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  {getModelIcon(mv.id)}
                  <div>
                    <h4 style={{ margin: 0, fontSize: "14px", color: "var(--text-primary)" }}>{mv.name}</h4>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                      Ensemble Weight: {(mv.weight * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                <span
                  style={{
                    padding: "3px 8px",
                    borderRadius: "4px",
                    fontSize: "11px",
                    fontWeight: "700",
                    background: isAi ? "rgba(239, 68, 68, 0.2)" : "rgba(34, 197, 94, 0.2)",
                    color: isAi ? "#f87171" : "#4ade80",
                    border: `1px solid ${isAi ? "#ef4444" : "#22c55e"}`
                  }}
                >
                  {isAi ? "Voted: AI" : "Voted: Human"}
                </span>
              </div>

              <p style={{ margin: 0, fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.4" }}>
                {getModelDescription(mv.id)}
              </p>

              {/* Confidence Progress Bar */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Inference Confidence</span>
                  <strong style={{ color: isAi ? "#f87171" : "#4ade80" }}>{confVal}%</strong>
                </div>
                <div style={{ width: "100%", height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "3px", overflow: "hidden" }}>
                  <div
                    style={{
                      width: `${confVal}%`,
                      height: "100%",
                      background: isAi ? "linear-gradient(90deg, #f97316, #ef4444)" : "linear-gradient(90deg, #10b981, #22c55e)",
                      borderRadius: "3px"
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Consensus Insights Footer */}
      <div
        style={{
          marginTop: "14px",
          padding: "10px 14px",
          borderRadius: "8px",
          background: "var(--bg-inner)",
          border: "1px solid var(--border-color)",
          fontSize: "12px",
          color: "var(--text-secondary)",
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}
      >
        <span style={{ fontSize: "14px" }}>💡</span>
        <span>
          <strong>Consensus Summary:</strong> {ai_votes} of 3 models classified this document as synthetic (
          {agreement_pct}% agreement). The ensemble combines deep transformer representations with n-gram dispersion to eliminate false positives on technical vocabulary.
        </span>
      </div>
    </div>
  );
};

export default ModelConsensusMatrix;
