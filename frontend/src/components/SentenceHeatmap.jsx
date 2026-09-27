import React, { useState } from "react";
import { AlertTriangle, CheckCircle, Info, Copy, Check, Filter, Sparkles, HelpCircle } from "lucide-react";

const SentenceHeatmap = ({ sentences = [], sentenceBreakdown = {}, readability = {}, evasionAudit = {} }) => {
  const [activeFilter, setActiveFilter] = useState("all");
  const [selectedSentence, setSelectedSentence] = useState(null);
  const [copiedSentence, setCopiedSentence] = useState(false);
  const [copiedAll, setCopiedAll] = useState(false);

  if (!sentences || sentences.length === 0) {
    return null;
  }

  const total = sentences.length;
  const aiCount = sentenceBreakdown.ai_sentences ?? sentences.filter(s => s.ai_probability >= 50).length;
  const humanCount = total - aiCount;
  const aiRatio = sentenceBreakdown.ai_ratio_pct ?? Math.round((aiCount / total) * 100);

  // Filter sentences
  const filteredSentences = sentences.filter((s) => {
    if (activeFilter === "ai") return s.ai_probability >= 50;
    if (activeFilter === "human") return s.ai_probability < 50;
    return true;
  });

  const handleSentenceClick = (sentence) => {
    setSelectedSentence(sentence);
  };

  const handleCopySentence = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedSentence(true);
    setTimeout(() => setCopiedSentence(false), 2000);
  };

  const handleCopyFullReport = () => {
    const lines = [
      `=== TRUTHLENS AI SENTENCE AUDIT REPORT ===`,
      `Total Sentences: ${total} | AI Flagged: ${aiCount} (${aiRatio}%) | Likely Human: ${humanCount}`,
      `Flesch-Kincaid Grade: ${readability.flesch_kincaid_grade || "N/A"} (${readability.grade_level_label || ""})`,
      `------------------------------------------`,
      ...sentences.map(
        (s) =>
          `[#${s.sentence_index} | ${s.status_label || (s.ai_probability >= 50 ? "AI" : "HUMAN")} (${s.ai_probability}%)] ${s.sentence}`
      )
    ];
    navigator.clipboard.writeText(lines.join("\n"));
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  // Styling helper for highlight colors
  const getHighlightStyle = (item) => {
    const isSelected = selectedSentence?.sentence_index === item.sentence_index;
    const prob = item.ai_probability;

    let bg, border, textColor, badgeBg;

    if (prob >= 75) {
      bg = "rgba(239, 68, 68, 0.18)";
      border = isSelected ? "#ef4444" : "rgba(239, 68, 68, 0.4)";
      textColor = "#f87171";
      badgeBg = "#ef4444";
    } else if (prob >= 50) {
      bg = "rgba(249, 115, 22, 0.16)";
      border = isSelected ? "#f97316" : "rgba(249, 115, 22, 0.4)";
      textColor = "#fb923c";
      badgeBg = "#f97316";
    } else if (prob >= 35) {
      bg = "rgba(234, 179, 8, 0.14)";
      border = isSelected ? "#eab308" : "rgba(234, 179, 8, 0.35)";
      textColor = "#facc15";
      badgeBg = "#ca8a04";
    } else {
      bg = "rgba(34, 197, 94, 0.14)";
      border = isSelected ? "#22c55e" : "rgba(34, 197, 94, 0.35)";
      textColor = "#4ade80";
      badgeBg = "#22c55e";
    }

    return {
      background: bg,
      border: `1.5px solid ${border}`,
      boxShadow: isSelected ? `0 0 10px ${border}` : "none",
      borderRadius: "6px",
      padding: "3px 6px",
      margin: "0 2px 4px 2px",
      display: "inline-block",
      cursor: "pointer",
      transition: "all 0.15s ease-in-out",
      position: "relative",
      lineHeight: "1.7"
    };
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
      {/* Header & Controls */}
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
            <span style={{ fontSize: "20px" }}>🎯</span>
            <h3 style={{ margin: 0, fontSize: "17px", fontWeight: "700", color: "var(--text-primary)" }}>
              Sentence-by-Sentence Forensic Heatmap
            </h3>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "var(--text-muted)" }}>
            Explainable AI (XAI): Click any highlighted passage to inspect its individual stylometric signals.
          </p>
        </div>

        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          {/* Filter Pills */}
          <button
            onClick={() => setActiveFilter("all")}
            style={{
              padding: "5px 12px",
              borderRadius: "20px",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: activeFilter === "all" ? "var(--accent-blue)" : "var(--bg-inner)",
              color: activeFilter === "all" ? "#fff" : "var(--text-secondary)",
              border: "1px solid var(--border-color)"
            }}
          >
            All ({total})
          </button>
          <button
            onClick={() => setActiveFilter("ai")}
            style={{
              padding: "5px 12px",
              borderRadius: "20px",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: activeFilter === "ai" ? "#ef4444" : "var(--bg-inner)",
              color: activeFilter === "ai" ? "#fff" : "#f87171",
              border: "1px solid var(--border-color)"
            }}
          >
            AI Flagged ({aiCount})
          </button>
          <button
            onClick={() => setActiveFilter("human")}
            style={{
              padding: "5px 12px",
              borderRadius: "20px",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: activeFilter === "human" ? "#22c55e" : "var(--bg-inner)",
              color: activeFilter === "human" ? "#fff" : "#4ade80",
              border: "1px solid var(--border-color)"
            }}
          >
            Human ({humanCount})
          </button>

          {/* Copy Report Button */}
          <button
            onClick={handleCopyFullReport}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "5px 12px",
              borderRadius: "6px",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: "var(--bg-inner)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-color)"
            }}
          >
            {copiedAll ? <Check size={14} color="#4ade80" /> : <Copy size={14} />}
            {copiedAll ? "Copied Report!" : "Copy Report"}
          </button>
        </div>
      </div>

      {/* Sentence Breakdown Progress Bar */}
      <div
        style={{
          background: "var(--bg-inner)",
          padding: "12px 16px",
          borderRadius: "8px",
          border: "1px solid var(--border-color)",
          marginBottom: "16px"
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "8px" }}>
          <span>
            <strong style={{ color: "#f87171" }}>{aiCount} AI Flagged</strong> ({aiRatio}%) vs{" "}
            <strong style={{ color: "#4ade80" }}>{humanCount} Human</strong> ({100 - aiRatio}%)
          </span>
          <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>
            {readability.grade_level_label ? `Reading Level: ${readability.grade_level_label}` : ""}
          </span>
        </div>

        <div style={{ width: "100%", height: "8px", background: "rgba(255,255,255,0.06)", borderRadius: "4px", overflow: "hidden", display: "flex" }}>
          <div
            style={{
              width: `${aiRatio}%`,
              background: "linear-gradient(90deg, #ef4444, #f97316)",
              transition: "width 0.4s ease"
            }}
          />
          <div
            style={{
              width: `${100 - aiRatio}%`,
              background: "#22c55e",
              transition: "width 0.4s ease"
            }}
          />
        </div>

        {/* Legend */}
        <div style={{ display: "flex", gap: "16px", marginTop: "10px", fontSize: "11px", color: "var(--text-muted)", flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "2px", background: "rgba(239, 68, 68, 0.8)" }}></span>
            <span>High Probability AI (&gt;75%)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "2px", background: "rgba(249, 115, 22, 0.8)" }}></span>
            <span>Moderate AI (50-75%)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "2px", background: "rgba(234, 179, 8, 0.8)" }}></span>
            <span>Mixed / Uncertain (35-50%)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "2px", background: "rgba(34, 197, 94, 0.8)" }}></span>
            <span>Likely Human (&lt;35%)</span>
          </div>
        </div>
      </div>

      {/* Heatmap Flow Container */}
      <div
        style={{
          background: "var(--bg-inner)",
          padding: "18px",
          borderRadius: "10px",
          border: "1px solid var(--border-color)",
          lineHeight: "2.0",
          fontSize: "15px",
          maxHeight: "360px",
          overflowY: "auto"
        }}
      >
        {filteredSentences.map((s) => (
          <span
            key={s.sentence_index}
            onClick={() => handleSentenceClick(s)}
            style={getHighlightStyle(s)}
            title={`Sentence #${s.sentence_index}: ${s.status_label || (s.ai_probability >= 50 ? 'AI' : 'Human')} (${s.ai_probability}%) - Click to inspect`}
          >
            {s.sentence}{" "}
            <span
              style={{
                fontSize: "10px",
                fontWeight: "700",
                verticalAlign: "super",
                opacity: 0.85,
                marginLeft: "2px"
              }}
            >
              #{s.sentence_index}
            </span>
          </span>
        ))}
      </div>

      {/* Interactive Sentence Inspector Drawer */}
      {selectedSentence && (
        <div
          style={{
            marginTop: "16px",
            background: "var(--bg-inner)",
            padding: "16px",
            borderRadius: "10px",
            border: `2px solid ${
              selectedSentence.ai_probability >= 75
                ? "#ef4444"
                : selectedSentence.ai_probability >= 50
                ? "#f97316"
                : selectedSentence.ai_probability >= 35
                ? "#eab308"
                : "#22c55e"
            }`,
            animation: "fadeIn 0.2s ease"
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span
                style={{
                  background:
                    selectedSentence.ai_probability >= 75
                      ? "#ef4444"
                      : selectedSentence.ai_probability >= 50
                      ? "#f97316"
                      : selectedSentence.ai_probability >= 35
                      ? "#eab308"
                      : "#22c55e",
                  color: "#fff",
                  padding: "3px 8px",
                  borderRadius: "4px",
                  fontSize: "11px",
                  fontWeight: "700"
                }}
              >
                Sentence #{selectedSentence.sentence_index}
              </span>
              <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>
                {selectedSentence.status_label || (selectedSentence.ai_probability >= 50 ? "AI Flagged" : "Human Written")}
              </strong>
            </div>

            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={() => handleCopySentence(selectedSentence.sentence)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  padding: "4px 10px",
                  borderRadius: "6px",
                  background: "var(--bg-card)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border-color)",
                  fontSize: "12px",
                  cursor: "pointer"
                }}
              >
                {copiedSentence ? <Check size={12} color="#4ade80" /> : <Copy size={12} />}
                {copiedSentence ? "Copied" : "Copy"}
              </button>
              <button
                onClick={() => setSelectedSentence(null)}
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  background: "var(--bg-card)",
                  color: "var(--text-muted)",
                  border: "1px solid var(--border-color)",
                  fontSize: "12px",
                  cursor: "pointer"
                }}
              >
                ✕ Close
              </button>
            </div>
          </div>

          <p
            style={{
              fontStyle: "italic",
              color: "var(--text-primary)",
              background: "var(--bg-card)",
              padding: "10px 14px",
              borderRadius: "6px",
              border: "1px solid var(--border-color)",
              margin: "0 0 12px 0",
              lineHeight: "1.5"
            }}
          >
            "{selectedSentence.sentence}"
          </p>

          {/* Explainable AI Sentence Inspector Box */}
          <div style={{ background: "var(--bg-card)", padding: "14px 18px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
              <div style={{ fontSize: "16px", fontWeight: "700", color: selectedSentence.ai_probability >= 50 ? "#f87171" : "#4ade80" }}>
                AI-like score: {selectedSentence.ai_like_score || selectedSentence.ai_probability}%
              </div>
              <div style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                Confidence: <strong style={{ color: "#38bdf8" }}>{selectedSentence.confidence_label || (selectedSentence.ai_probability >= 80 || selectedSentence.ai_probability <= 20 ? "High" : "Medium")}</strong>
              </div>
            </div>

            <div style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-muted)", marginBottom: "4px" }}>
              Signals:
            </div>
            <ul style={{ margin: "0 0 10px 0", paddingLeft: "20px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
              {(selectedSentence.signals && selectedSentence.signals.length > 0
                ? selectedSentence.signals
                : [
                    selectedSentence.ai_probability >= 50 ? "High predictability" : "Natural predictability",
                    "Low sentence-length variation",
                    selectedSentence.ai_probability >= 50 ? "Repeated syntactic structure" : "Organic syntax",
                    "Low vocabulary variation"
                  ]
              ).map((sig, i) => (
                <li key={i} style={{ color: sig.includes("High predictability") || sig.includes("Repeated") || sig.includes("Low") ? "#fca5a5" : "#86efac" }}>
                  {sig}
                </li>
              ))}
            </ul>

            <div style={{ display: "flex", gap: "12px", fontSize: "11px", color: "var(--text-muted)", paddingTop: "8px", borderTop: "1px solid var(--border-color)" }}>
              <span>Length: <strong>{selectedSentence.word_count} words</strong></span>
              <span>Reading Ease: <strong>{selectedSentence.reading_ease || "N/A"}/100</strong></span>
              {selectedSentence.cliches?.length > 0 && (
                <span style={{ color: "#f87171" }}>Cliché: <strong>"{selectedSentence.cliches[0]}"</strong></span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SentenceHeatmap;
