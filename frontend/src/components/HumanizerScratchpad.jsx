import React, { useState } from "react";
import { Sparkles, RefreshCw, ArrowRight, CheckCircle, TrendingDown, Wand2, Copy } from "lucide-react";
import { analyzeText } from "../services/api";

const HumanizerScratchpad = ({ initialText = "", originalResult = null, selectedModel = "all" }) => {
  const [scratchText, setScratchText] = useState(initialText);
  const [loading, setLoading] = useState(false);
  const [newResult, setNewResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const origProb =
    originalResult?.confidence !== null && originalResult?.confidence !== undefined
      ? Math.round(originalResult.confidence * 100)
      : null;

  const currentProb =
    newResult?.confidence !== null && newResult?.confidence !== undefined
      ? Math.round(newResult.confidence * 100)
      : null;

  const probDiff = origProb !== null && currentProb !== null ? origProb - currentProb : null;

  const handleAnalyzeScratchpad = async () => {
    if (!scratchText.trim()) return;
    setLoading(true);
    try {
      const res = await analyzeText(scratchText, selectedModel);
      setNewResult(res);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(scratchText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      style={{
        background: "var(--bg-card)",
        padding: "24px",
        borderRadius: "12px",
        border: "1px solid var(--border-color)",
        marginTop: "20px"
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
            <span style={{ fontSize: "20px" }}>✍️</span>
            <h3 style={{ margin: 0, fontSize: "17px", fontWeight: "700", color: "var(--text-primary)" }}>
              Live Humanizer & Rewriter Scratchpad
            </h3>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "var(--text-muted)" }}>
            Rewrite passages to increase natural human burstiness, replace AI cliches, and watch the detection score drop live.
          </p>
        </div>

        {/* Score Comparison Badge */}
        {origProb !== null && currentProb !== null && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              background: "var(--bg-inner)",
              padding: "8px 16px",
              borderRadius: "20px",
              border: "1px solid var(--border-color)"
            }}
          >
            <div style={{ textAlign: "center" }}>
              <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>ORIGINAL AI</span>
              <div style={{ fontSize: "14px", fontWeight: "700", color: "#f87171" }}>{origProb}%</div>
            </div>

            <ArrowRight size={16} color="var(--text-muted)" />

            <div style={{ textAlign: "center" }}>
              <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>REVISED AI</span>
              <div style={{ fontSize: "14px", fontWeight: "700", color: currentProb < 50 ? "#4ade80" : "#fb923c" }}>
                {currentProb}%
              </div>
            </div>

            {probDiff !== null && probDiff > 0 && (
              <div
                style={{
                  background: "rgba(34, 197, 94, 0.15)",
                  color: "#4ade80",
                  padding: "4px 10px",
                  borderRadius: "12px",
                  fontSize: "12px",
                  fontWeight: "700",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px"
                }}
              >
                <TrendingDown size={14} /> -{probDiff}% AI Score
              </div>
            )}
          </div>
        )}
      </div>

      {/* Split Comparison View */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
        {/* Left: Original Reference */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
              ORIGINAL TEXT (READ-ONLY REFERENCE)
            </span>
            {origProb !== null && (
              <span style={{ fontSize: "11px", color: origProb >= 50 ? "#f87171" : "#4ade80", fontWeight: "700" }}>
                Baseline AI: {origProb}%
              </span>
            )}
          </div>
          <div
            style={{
              padding: "14px",
              borderRadius: "8px",
              background: "var(--bg-inner)",
              border: "1px solid var(--border-color)",
              color: "var(--text-muted)",
              fontSize: "14px",
              lineHeight: "1.6",
              height: "240px",
              overflowY: "auto",
              whiteSpace: "pre-wrap"
            }}
          >
            {initialText || "No original text submitted yet. Analyze text in workspace first."}
          </div>
        </div>

        {/* Right: Editable Scratchpad */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: "600", color: "#38bdf8" }}>
              EDITABLE REWRITE SCRATCHPAD
            </span>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={handleCopy}
                style={{
                  padding: "3px 8px",
                  borderRadius: "4px",
                  background: "var(--bg-inner)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border-color)",
                  fontSize: "11px",
                  cursor: "pointer"
                }}
              >
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
          </div>

          <textarea
            value={scratchText}
            onChange={(e) => setScratchText(e.target.value)}
            placeholder="Edit, rewrite, and vary sentence lengths here..."
            rows={9}
            style={{
              width: "100%",
              padding: "14px",
              borderRadius: "8px",
              background: "var(--bg-inner)",
              color: "var(--text-primary)",
              border: "1px solid #38bdf8",
              fontSize: "14px",
              lineHeight: "1.6",
              height: "240px",
              resize: "none",
              fontFamily: "inherit"
            }}
          />
        </div>
      </div>

      {/* Action Controls & Humanizing Tips */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "16px",
          flexWrap: "wrap",
          gap: "12px"
        }}
      >
        <div style={{ display: "flex", gap: "16px", fontSize: "12px", color: "var(--text-muted)" }}>
          <span>
            Words: <strong style={{ color: "var(--text-primary)" }}>{scratchText.split(/\s+/).filter(Boolean).length}</strong>
          </span>
          <span>
            Characters: <strong style={{ color: "var(--text-primary)" }}>{scratchText.length}</strong>
          </span>
        </div>

        <button
          onClick={handleAnalyzeScratchpad}
          disabled={loading || !scratchText.trim()}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "8px 20px",
            borderRadius: "6px",
            background: loading ? "var(--text-muted)" : "var(--accent-gradient)",
            color: "#ffffff",
            fontWeight: "600",
            border: "none",
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? <RefreshCw size={14} className="animate-spin" /> : <Wand2 size={14} />}
          {loading ? "Re-Evaluating..." : "Test Rewritten Text Score"}
        </button>
      </div>

      {/* Tips Box */}
      <div
        style={{
          marginTop: "16px",
          padding: "12px 16px",
          borderRadius: "8px",
          background: "var(--bg-inner)",
          border: "1px solid var(--border-color)",
          fontSize: "12px",
          color: "var(--text-secondary)",
          lineHeight: "1.5"
        }}
      >
        <strong style={{ color: "var(--text-primary)" }}>💡 Proven Stylometric Humanizing Strategies:</strong>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "8px", marginTop: "8px" }}>
          <div>• <strong>Vary Sentence Length:</strong> Mix 5-word sentences with longer 25-word complex sentences to raise burstiness.</div>
          <div>• <strong>Purge Transition Cliches:</strong> Delete <em>"moreover"</em>, <em>"delve into"</em>, <em>"testament to"</em>, <em>"in conclusion"</em>.</div>
          <div>• <strong>Inject Personal Voice:</strong> Add sensory details, colloquial phrasing, or specific first-person observations.</div>
        </div>
      </div>
    </div>
  );
};

export default HumanizerScratchpad;
