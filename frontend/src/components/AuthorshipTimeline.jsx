import React, { useState } from "react";
import { GitCommit, ArrowRight, AlertCircle, CheckCircle, ChevronDown, ChevronUp, UserCheck, Bot } from "lucide-react";

const AuthorshipTimeline = ({ timeline }) => {
  const [expandedBlock, setExpandedBlock] = useState(null);

  if (!timeline || !timeline.blocks || timeline.blocks.length === 0) {
    return null;
  }

  const {
    is_mixed_authorship,
    total_blocks,
    blocks = [],
    transitions = [],
    distribution = {},
    summary
  } = timeline;

  const getStatusColor = (classification) => {
    if (classification === "AI-like") return { bg: "rgba(239, 68, 68, 0.15)", border: "#ef4444", text: "#f87171" };
    if (classification === "Human-like") return { bg: "rgba(16, 185, 129, 0.15)", border: "#10b981", text: "#34d399" };
    return { bg: "rgba(245, 158, 11, 0.15)", border: "#f59e0b", text: "#fbbf24" };
  };

  return (
    <div
      style={{
        marginTop: "20px",
        background: "var(--bg-card)",
        borderRadius: "12px",
        border: "1px solid var(--border-color)",
        overflow: "hidden"
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px 20px",
          borderBottom: "1px solid var(--border-color)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "10px"
        }}
      >
        <div>
          <h3 style={{ margin: "0 0 4px 0", fontSize: "17px", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
            <GitCommit size={18} color="#a855f7" />
            Mixed Authorship Timeline & Transitions
          </h3>
          <p style={{ margin: 0, fontSize: "12px", color: "var(--text-muted)" }}>
            Paragraph-by-paragraph segment analysis mapping human-to-machine stylistic transitions
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          {is_mixed_authorship ? (
            <span
              style={{
                background: "rgba(245, 158, 11, 0.15)",
                border: "1px solid #f59e0b",
                color: "#fbbf24",
                padding: "4px 10px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: "700",
                display: "inline-flex",
                alignItems: "center",
                gap: "5px"
              }}
            >
              <AlertCircle size={14} />
              Mixed Authorship Detected ({transitions.length} Transition{transitions.length !== 1 ? "s" : ""})
            </span>
          ) : (
            <span
              style={{
                background: "rgba(16, 185, 129, 0.15)",
                border: "1px solid #10b981",
                color: "#34d399",
                padding: "4px 10px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: "700",
                display: "inline-flex",
                alignItems: "center",
                gap: "5px"
              }}
            >
              <CheckCircle size={14} />
              Single-Source Continuity
            </span>
          )}
        </div>
      </div>

      <div style={{ padding: "20px" }}>
        {/* Authorship Distribution Bar */}
        <div style={{ marginBottom: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "6px" }}>
            <span>
              <strong style={{ color: "#34d399" }}>{distribution.human_blocks_pct || 0}%</strong> Human-like
            </span>
            <span>
              <strong style={{ color: "#fbbf24" }}>{distribution.mixed_blocks_pct || 0}%</strong> Mixed/Uncertain
            </span>
            <span>
              <strong style={{ color: "#f87171" }}>{distribution.ai_blocks_pct || 0}%</strong> AI-like
            </span>
          </div>
          <div style={{ width: "100%", height: "8px", background: "var(--bg-inner)", borderRadius: "4px", overflow: "hidden", display: "flex" }}>
            <div style={{ width: `${distribution.human_blocks_pct || 0}%`, height: "100%", background: "#34d399" }} />
            <div style={{ width: `${distribution.mixed_blocks_pct || 0}%`, height: "100%", background: "#f59e0b" }} />
            <div style={{ width: `${distribution.ai_blocks_pct || 0}%`, height: "100%", background: "#ef4444" }} />
          </div>
        </div>

        {/* Timeline Visualization Blocks */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              overflowX: "auto",
              paddingBottom: "10px"
            }}
          >
            {blocks.map((b, idx) => {
              const style = getStatusColor(b.classification);
              const transitionAfter = transitions.find(t => t.from_block === b.block_index);

              return (
                <React.Fragment key={idx}>
                  <div
                    onClick={() => setExpandedBlock(expandedBlock === b.block_index ? null : b.block_index)}
                    style={{
                      flexShrink: 0,
                      minWidth: "160px",
                      background: expandedBlock === b.block_index ? style.bg : "var(--bg-inner)",
                      border: `1.5px solid ${style.border}`,
                      borderRadius: "8px",
                      padding: "10px 14px",
                      cursor: "pointer",
                      transition: "all 0.2s"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                      <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-muted)" }}>
                        {b.label}
                      </span>
                      <span style={{ fontSize: "11px", fontWeight: "700", color: style.text }}>
                        {b.ai_probability}% AI
                      </span>
                    </div>

                    <div style={{ fontSize: "12px", fontWeight: "600", color: style.text, marginBottom: "4px", display: "flex", alignItems: "center", gap: "4px" }}>
                      {b.classification === "AI-like" ? <Bot size={13} /> : <UserCheck size={13} />}
                      {b.classification}
                    </div>

                    <p style={{ margin: 0, fontSize: "11px", color: "var(--text-secondary)", lineHeight: "1.3" }}>
                      {b.text_snippet}
                    </p>
                  </div>

                  {transitionAfter && (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "2px", flexShrink: 0, padding: "0 4px" }}>
                      <span style={{ fontSize: "10px", fontWeight: "700", color: "#f59e0b" }}>
                        {transitionAfter.delta_probability > 0 ? `+${transitionAfter.delta_probability}%` : `${transitionAfter.delta_probability}%`}
                      </span>
                      <ArrowRight size={16} color="#f59e0b" />
                      <span style={{ fontSize: "9px", color: "var(--text-muted)" }}>Shift</span>
                    </div>
                  )}

                  {!transitionAfter && idx < blocks.length - 1 && (
                    <div style={{ flexShrink: 0, padding: "0 2px" }}>
                      <ArrowRight size={14} color="var(--text-muted)" />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* Expanded Block Details */}
          {expandedBlock !== null && (() => {
            const block = blocks.find(b => b.block_index === expandedBlock);
            if (!block) return null;
            const style = getStatusColor(block.classification);

            return (
              <div
                style={{
                  background: "var(--bg-inner)",
                  border: `1px solid ${style.border}`,
                  borderRadius: "8px",
                  padding: "16px",
                  marginTop: "8px"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <h4 style={{ margin: 0, fontSize: "14px", color: style.text, display: "flex", alignItems: "center", gap: "6px" }}>
                    {block.label} Detailed Inspection
                  </h4>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {block.word_count} words • {block.sentence_count} sentences • Confidence: <strong>{block.confidence}</strong>
                  </span>
                </div>

                <p style={{ margin: "0 0 10px 0", fontSize: "13px", color: "var(--text-primary)", fontStyle: "italic", lineHeight: "1.5" }}>
                  "{block.full_text}"
                </p>

                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                  {block.signals.map((s, idx) => (
                    <span key={idx} style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", padding: "3px 8px", borderRadius: "4px", fontSize: "11px", color: "var(--text-secondary)" }}>
                      • {s}
                    </span>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Transition Summary Text */}
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "8px", fontStyle: "italic" }}>
            📌 <strong>Authorship Assessment:</strong> {summary}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthorshipTimeline;
