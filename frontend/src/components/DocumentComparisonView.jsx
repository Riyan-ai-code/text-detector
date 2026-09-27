import React, { useState } from "react";
import axios from "axios";
import { Scale, ArrowRight, FileText, CheckCircle, AlertTriangle, Sparkles } from "lucide-react";
import { API_URL } from "../services/api";

const SAMPLE_A = (
  "I spent most of last weekend rummaging through my grandfather's attic, searching for an old wooden toolbox he used to carry everywhere. " +
  "The air up there smelled like cedar and aged paper, and beneath a stack of dusty canvas tarps, I finally found it! " +
  "Opening the rusted brass latch brought back a flood of memories—summer afternoons building lopsided birdhouses on the back porch while listening " +
  "to the hum of cicadas in the maple trees. Dad used to say quality tools outlive their owners, and he wasn't wrong."
);

const SAMPLE_B = (
  "Artificial intelligence has revolutionized modern enterprise workflows by automating repetitive tasks and augmenting human decision-making. " +
  "Through advanced deep learning architectures and extensive pretraining across web-scale text corpora, large language models exhibit " +
  "remarkable proficiency across diverse domains. In essence, this technological revolution stands as a testament to human ingenuity and underscores " +
  "the vital importance of ethical governance as we delve into an automated future."
);

const DocumentComparisonView = ({ onBackToWorkspace }) => {
  const [docA, setDocA] = useState(SAMPLE_A);
  const [docB, setDocB] = useState(SAMPLE_B);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    if (!docA.trim() || !docB.trim()) {
      alert("Please provide text for both Document A and Document B.");
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/v1/text/compare`, {
        document_a: docA,
        document_b: docB
      });
      setResult(res.data);
    } catch (e) {
      console.error("Comparison failed", e);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Header */}
      <div
        style={{
          background: "var(--bg-card)",
          padding: "20px 24px",
          borderRadius: "12px",
          border: "1px solid var(--border-color)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px"
        }}
      >
        <div>
          <h2 style={{ margin: "0 0 6px 0", fontSize: "20px", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
            <Scale size={22} color="#38bdf8" />
            Side-by-Side Document Comparison Mode
          </h2>
          <p style={{ margin: 0, fontSize: "14px", color: "var(--text-muted)" }}>
            Forensically contrast two drafts, essays, or submissions to pinpoint divergence in AI likelihood, vocabulary, burstiness, and style.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={handleCompare}
            disabled={loading}
            style={{
              padding: "10px 20px",
              borderRadius: "8px",
              background: "var(--accent-gradient)",
              color: "#fff",
              border: "none",
              fontSize: "14px",
              fontWeight: "700",
              cursor: "pointer"
            }}
          >
            {loading ? "Comparing Forensic Signals..." : "⚖️ Compare Documents"}
          </button>
          {onBackToWorkspace && (
            <button
              onClick={onBackToWorkspace}
              style={{
                padding: "10px 16px",
                borderRadius: "8px",
                background: "var(--bg-inner)",
                color: "var(--text-primary)",
                border: "1px solid var(--border-color)",
                fontSize: "14px",
                fontWeight: "600",
                cursor: "pointer"
              }}
            >
              ← Back to Workspace
            </button>
          )}
        </div>
      </div>

      {/* Dual Input Panels */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
        {/* Document A Input */}
        <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <h3 style={{ margin: 0, fontSize: "16px", color: "#38bdf8", display: "flex", alignItems: "center", gap: "6px" }}>
              <FileText size={16} /> Document A
            </h3>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              {docA.split(/\s+/).filter(Boolean).length} words
            </span>
          </div>
          <textarea
            value={docA}
            onChange={(e) => setDocA(e.target.value)}
            rows={10}
            style={{
              width: "100%",
              padding: "12px",
              borderRadius: "8px",
              background: "var(--bg-inner)",
              border: "1px solid var(--border-color)",
              color: "var(--text-primary)",
              fontSize: "13px",
              fontFamily: "inherit",
              resize: "vertical"
            }}
          />
        </div>

        {/* Document B Input */}
        <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <h3 style={{ margin: 0, fontSize: "16px", color: "#c084fc", display: "flex", alignItems: "center", gap: "6px" }}>
              <FileText size={16} /> Document B
            </h3>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              {docB.split(/\s+/).filter(Boolean).length} words
            </span>
          </div>
          <textarea
            value={docB}
            onChange={(e) => setDocB(e.target.value)}
            rows={10}
            style={{
              width: "100%",
              padding: "12px",
              borderRadius: "8px",
              background: "var(--bg-inner)",
              border: "1px solid var(--border-color)",
              color: "var(--text-primary)",
              fontSize: "13px",
              fontFamily: "inherit",
              resize: "vertical"
            }}
          />
        </div>
      </div>

      {/* Comparison Results */}
      {result && (
        <div style={{ background: "var(--bg-card)", padding: "24px", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
          <h3 style={{ margin: "0 0 16px 0", fontSize: "18px", color: "var(--text-primary)" }}>
            Forensic Comparison Matrix
          </h3>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "24px" }}>
            {/* Document A Summary Box */}
            <div style={{ background: "var(--bg-inner)", padding: "20px", borderRadius: "10px", border: "1.5px solid #38bdf8" }}>
              <div style={{ fontSize: "14px", fontWeight: "700", color: "#38bdf8", marginBottom: "12px" }}>
                DOCUMENT A SUMMARY
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "14px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>AI-like:</span>
                  <strong style={{ color: result.document_a.ai_like_pct >= 50 ? "#f87171" : "#4ade80", fontSize: "16px" }}>
                    {result.document_a.ai_like_pct}%
                  </strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Vocabulary:</span>
                  <strong>{result.document_a.vocabulary_diversity}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Burstiness:</span>
                  <strong>{result.document_a.burstiness}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Style deviation:</span>
                  <strong>{result.document_a.style_deviation_pct}%</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--text-muted)" }}>
                  <span>Mean Sentence Length:</span>
                  <span>{result.document_a.avg_sentence_length} words</span>
                </div>
              </div>
            </div>

            {/* Document B Summary Box */}
            <div style={{ background: "var(--bg-inner)", padding: "20px", borderRadius: "10px", border: "1.5px solid #c084fc" }}>
              <div style={{ fontSize: "14px", fontWeight: "700", color: "#c084fc", marginBottom: "12px" }}>
                DOCUMENT B SUMMARY
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "14px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>AI-like:</span>
                  <strong style={{ color: result.document_b.ai_like_pct >= 50 ? "#f87171" : "#4ade80", fontSize: "16px" }}>
                    {result.document_b.ai_like_pct}%
                  </strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Vocabulary:</span>
                  <strong>{result.document_b.vocabulary_diversity}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Burstiness:</span>
                  <strong>{result.document_b.burstiness}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Style deviation:</span>
                  <strong>{result.document_b.style_deviation_pct}%</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--text-muted)" }}>
                  <span>Mean Sentence Length:</span>
                  <span>{result.document_b.avg_sentence_length} words</span>
                </div>
              </div>
            </div>
          </div>

          {/* Divergence Insights */}
          <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <h4 style={{ margin: "0 0 8px 0", fontSize: "14px", color: "var(--text-primary)" }}>
              Divergence Insights & Major Differences:
            </h4>
            <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
              {result.divergence_insights.map((insight, idx) => (
                <li key={idx}>{insight}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentComparisonView;
