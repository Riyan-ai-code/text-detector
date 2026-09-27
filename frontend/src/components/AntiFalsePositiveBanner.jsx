import React from "react";
import { AlertTriangle, ShieldCheck, Info, HelpCircle, CheckCircle } from "lucide-react";

const AntiFalsePositiveBanner = ({ calibration, counts }) => {
  if (!calibration) return null;

  const {
    calibrated_confidence = "MEDIUM",
    reliability_index = 80,
    warnings = [],
    domain_caveats = [],
    anti_false_positive_disclaimer,
    executive_assessment
  } = calibration;

  const confBadgeStyle = {
    HIGH: { bg: "rgba(16, 185, 129, 0.15)", border: "#10b981", color: "#34d399", label: "High Forensic Confidence" },
    MEDIUM: { bg: "rgba(245, 158, 11, 0.15)", border: "#f59e0b", color: "#fbbf24", label: "Medium Confidence (Moderate Variance)" },
    LOW: { bg: "rgba(239, 68, 68, 0.15)", border: "#ef4444", color: "#f87171", label: "Low Confidence (High Variance / Short Sample)" }
  }[calibrated_confidence] || { bg: "rgba(148, 163, 184, 0.15)", border: "#64748b", color: "#94a3b8", label: "Uncalibrated" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginBottom: "20px" }}>
      {/* 1. Core Confidence & Uncertainty Card */}
      <div
        style={{
          background: "var(--bg-card)",
          border: `1.5px solid ${confBadgeStyle.border}`,
          borderRadius: "12px",
          padding: "16px 20px"
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
              <span
                style={{
                  background: confBadgeStyle.bg,
                  color: confBadgeStyle.color,
                  border: `1px solid ${confBadgeStyle.border}`,
                  padding: "4px 10px",
                  borderRadius: "6px",
                  fontSize: "12px",
                  fontWeight: "700",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "5px"
                }}
              >
                {calibrated_confidence === "HIGH" ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
                {confBadgeStyle.label}
              </span>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Reliability Index: <strong style={{ color: confBadgeStyle.color }}>{reliability_index}/100</strong>
              </span>
            </div>

            <p style={{ margin: "4px 0 0 0", fontSize: "14px", color: "var(--text-primary)", fontWeight: "500", lineHeight: "1.5" }}>
              {executive_assessment}
            </p>
          </div>

          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            {counts && (
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>DOCUMENT SIZE</span>
                <span style={{ fontSize: "13px", fontWeight: "700", color: "var(--text-primary)" }}>
                  {counts.word_count || 0} words • {counts.sentence_count || 0} sentences
                </span>
              </div>
            )}
          </div>
        </div>

        {/* 2. Critical Sample-Size & Disagreement Warnings */}
        {warnings.length > 0 && (
          <div style={{ marginTop: "14px", display: "flex", flexDirection: "column", gap: "8px" }}>
            {warnings.map((w, idx) => (
              <div
                key={idx}
                style={{
                  background: w.severity === "HIGH" ? "rgba(239, 68, 68, 0.12)" : "rgba(245, 158, 11, 0.12)",
                  borderLeft: `4px solid ${w.severity === "HIGH" ? "#ef4444" : "#f59e0b"}`,
                  padding: "8px 12px",
                  borderRadius: "4px 8px 8px 4px",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  fontSize: "13px",
                  color: w.severity === "HIGH" ? "#fca5a5" : "#fde68a"
                }}
              >
                <AlertTriangle size={16} style={{ flexShrink: 0 }} />
                <span>{w.message}</span>
              </div>
            ))}
          </div>
        )}

        {/* 3. Domain Bias Disclaimers (Academic, Legal) */}
        {domain_caveats.length > 0 && (
          <div style={{ marginTop: "12px", display: "flex", flexDirection: "column", gap: "6px" }}>
            {domain_caveats.map((c, idx) => (
              <div
                key={idx}
                style={{
                  background: "rgba(56, 189, 248, 0.08)",
                  border: "1px solid rgba(56, 189, 248, 0.3)",
                  padding: "8px 12px",
                  borderRadius: "6px",
                  fontSize: "12px",
                  color: "var(--text-secondary)",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "8px"
                }}
              >
                <Info size={15} color="#38bdf8" style={{ flexShrink: 0, marginTop: "2px" }} />
                <div>
                  <strong style={{ color: "#38bdf8" }}>{c.domain} ({c.risk}): </strong>
                  {c.explanation}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 4. Mandatory Ground Rule Disclaimer */}
        <div
          style={{
            marginTop: "12px",
            paddingTop: "10px",
            borderTop: "1px solid var(--border-color)",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "12px",
            color: "var(--text-muted)",
            fontStyle: "italic"
          }}
        >
          <HelpCircle size={14} style={{ flexShrink: 0 }} />
          <span>{anti_false_positive_disclaimer}</span>
        </div>
      </div>
    </div>
  );
};

export default AntiFalsePositiveBanner;
