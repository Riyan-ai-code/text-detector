import { useState } from "react";
import { analyzePlagiarism, getPlagiarismCorpus } from "../services/api";
import { Search, BookOpen, AlertTriangle, CheckCircle, Sliders, ExternalLink, RefreshCw } from "lucide-react";

const SAMPLES = {
  transformer: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The Transformer relies entirely on self-attention mechanisms to compute representations without sequence-aligned RNNs.",
  turing_paraphrase: "We propose replacing the inquiry of whether mechanical computers can think with an alternative setup framed as an imitation game.",
  original: "Yesterday evening my younger cousin baked blueberry scones with cinnamon sugar while we listened to acoustic jazz on an old battery-operated radio."
};

const MATCH_TYPE_STYLES = {
  exact: { bg: "rgba(239, 68, 68, 0.15)", color: "#f87171", border: "1px solid #ef4444", label: "EXACT MATCH" },
  near_duplicate: { bg: "rgba(245, 158, 11, 0.15)", color: "#fbbf24", border: "1px solid #f59e0b", label: "NEAR DUPLICATE" },
  paraphrase: { bg: "rgba(59, 130, 246, 0.15)", color: "#60a5fa", border: "1px solid #3b82f6", label: "PARAPHRASE" },
  semantic: { bg: "rgba(168, 85, 247, 0.15)", color: "#c084fc", border: "1px solid #a855f7", label: "SEMANTIC ALIGNMENT" }
};

const PlagiarismViewer = ({ onBackToWorkspace }) => {
  const [text, setText] = useState(SAMPLES.transformer);
  const [threshold, setThreshold] = useState(0.35);
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showCorpus, setShowCorpus] = useState(false);
  const [corpusList, setCorpusList] = useState([]);
  const [loadingCorpus, setLoadingCorpus] = useState(false);

  const handleScan = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await analyzePlagiarism(text, threshold, topK);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err?.message || "Failed to scan text for plagiarism.");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadCorpus = async () => {
    setShowCorpus(!showCorpus);
    if (!showCorpus && corpusList.length === 0) {
      setLoadingCorpus(true);
      try {
        const data = await getPlagiarismCorpus();
        setCorpusList(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingCorpus(false);
      }
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Header Banner */}
      <div style={{
        background: "var(--bg-card)",
        padding: "24px",
        borderRadius: "12px",
        border: "1px solid var(--border-color)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "16px"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
            <span style={{
              background: "rgba(59, 130, 246, 0.2)",
              color: "#60a5fa",
              padding: "4px 10px",
              borderRadius: "6px",
              fontSize: "12px",
              fontWeight: "bold",
              letterSpacing: "0.5px"
            }}>
              SYSTEM 2: HYBRID RETRIEVAL
            </span>
            <h2 style={{ margin: 0, color: "var(--text-primary)", fontSize: "22px" }}>
              Semantic Plagiarism & Paraphrase Engine
            </h2>
          </div>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "14px" }}>
            Directional stem containment, n-gram concordance, and sentence-level passage alignment across indexed academic literature.
          </p>
        </div>

        <div style={{ display: "flex", gap: "12px" }}>
          <button
            onClick={handleLoadCorpus}
            style={{
              padding: "10px 16px",
              borderRadius: "8px",
              background: showCorpus ? "rgba(59, 130, 246, 0.25)" : "var(--bg-inner)",
              color: "#60a5fa",
              border: "1px solid #3b82f6",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "14px",
              fontWeight: "600"
            }}
          >
            <BookOpen size={16} />
            {showCorpus ? "Hide Corpus" : "View Indexed Literature"}
          </button>
          {onBackToWorkspace && (
            <button
              onClick={onBackToWorkspace}
              style={{
                padding: "10px 16px",
                borderRadius: "8px",
                background: "var(--bg-inner)",
                color: "var(--text-secondary)",
                border: "1px solid var(--border-color)",
                cursor: "pointer",
                fontSize: "14px"
              }}
            >
              ← Back to Workspace
            </button>
          )}
        </div>
      </div>

      {/* Indexed Corpus Catalog Drawer */}
      {showCorpus && (
        <div style={{
          background: "var(--bg-card)",
          padding: "20px",
          borderRadius: "12px",
          border: "1px solid #3b82f6",
          animation: "fadeIn 0.3s ease"
        }}>
          <h3 style={{ margin: "0 0 12px 0", color: "#60a5fa", fontSize: "16px" }}>
            📚 Indexed Reference Corpus ({corpusList.length} Landmark Sources)
          </h3>
          {loadingCorpus ? (
            <p style={{ color: "var(--text-muted)" }}>Loading corpus catalog...</p>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "12px" }}>
              {corpusList.map((doc) => (
                <div key={doc.id} style={{
                  background: "var(--bg-inner)",
                  padding: "12px",
                  borderRadius: "8px",
                  border: "1px solid var(--border-color)"
                }}>
                  <div style={{ fontSize: "11px", color: "#60a5fa", fontWeight: "bold" }}>{doc.category}</div>
                  <div style={{ fontWeight: "600", fontSize: "13px", color: "var(--text-primary)", margin: "4px 0" }}>{doc.title}</div>
                  <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>Author: {doc.author} • {doc.word_count} words</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Input & Tuning Area */}
      <div style={{
        background: "var(--bg-card)",
        padding: "24px",
        borderRadius: "12px",
        border: "1px solid var(--border-color)",
        display: "flex",
        flexDirection: "column",
        gap: "16px"
      }}>
        {/* Sample Presets */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <span style={{ fontSize: "13px", color: "var(--text-muted)", fontWeight: "600" }}>Quick Presets:</span>
          <button
            onClick={() => setText(SAMPLES.transformer)}
            style={{
              padding: "6px 12px",
              borderRadius: "6px",
              background: "var(--bg-inner)",
              border: "1px solid var(--border-color)",
              color: "var(--text-secondary)",
              fontSize: "12px",
              cursor: "pointer"
            }}
          >
            📑 Verbatim Transformer Excerpt
          </button>
          <button
            onClick={() => setText(SAMPLES.turing_paraphrase)}
            style={{
              padding: "6px 12px",
              borderRadius: "6px",
              background: "var(--bg-inner)",
              border: "1px solid var(--border-color)",
              color: "var(--text-secondary)",
              fontSize: "12px",
              cursor: "pointer"
            }}
          >
            🔄 Turing Paraphrase Test
          </button>
          <button
            onClick={() => setText(SAMPLES.original)}
            style={{
              padding: "6px 12px",
              borderRadius: "6px",
              background: "var(--bg-inner)",
              border: "1px solid var(--border-color)",
              color: "var(--text-secondary)",
              fontSize: "12px",
              cursor: "pointer"
            }}
          >
            ✍️ Authentic Original Prose
          </button>
        </div>

        {/* Text Area */}
        <textarea
          rows={6}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste or type document text to scan for verbatim duplication or semantic paraphrasing..."
          style={{
            width: "100%",
            padding: "16px",
            borderRadius: "8px",
            background: "var(--bg-inner)",
            border: "1px solid var(--border-color)",
            color: "var(--text-primary)",
            fontSize: "14px",
            lineHeight: "1.6",
            resize: "vertical",
            fontFamily: "inherit",
            boxSizing: "border-box"
          }}
        />

        {/* Controls Bar */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
          paddingTop: "8px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Sliders size={16} color="var(--text-muted)" />
              <label style={{ fontSize: "13px", color: "var(--text-secondary)", fontWeight: "600" }}>
                Threshold: <span style={{ color: "#60a5fa" }}>{Math.round(threshold * 100)}%</span>
              </label>
              <input
                type="range"
                min="0.20"
                max="0.80"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                style={{ width: "120px", cursor: "pointer" }}
              />
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <label style={{ fontSize: "13px", color: "var(--text-secondary)", fontWeight: "600" }}>Top-K:</label>
              <select
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value, 10))}
                style={{
                  padding: "6px 10px",
                  borderRadius: "6px",
                  background: "var(--bg-inner)",
                  border: "1px solid var(--border-color)",
                  color: "var(--text-primary)",
                  fontSize: "13px"
                }}
              >
                <option value={3}>Top 3</option>
                <option value={5}>Top 5</option>
                <option value={8}>Top 8</option>
              </select>
            </div>

            <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
              {text.trim() ? text.trim().split(/\s+/).length : 0} words • {text.length} chars
            </span>
          </div>

          <button
            onClick={handleScan}
            disabled={loading || !text.trim()}
            style={{
              padding: "12px 28px",
              borderRadius: "8px",
              background: "linear-gradient(135deg, #2563eb, #3b82f6)",
              color: "#ffffff",
              border: "none",
              fontWeight: "600",
              cursor: loading || !text.trim() ? "not-allowed" : "pointer",
              opacity: loading || !text.trim() ? 0.6 : 1,
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "15px"
            }}
          >
            {loading ? <RefreshCw size={16} className="spin" /> : <Search size={16} />}
            {loading ? "Analyzing Concordance..." : "Scan For Plagiarism"}
          </button>
        </div>

        {error && (
          <div style={{ padding: "12px", background: "rgba(239, 68, 68, 0.15)", border: "1px solid #ef4444", borderRadius: "8px", color: "#f87171", fontSize: "14px" }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Results View */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Summary Metric Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
            {/* Overall Similarity */}
            <div style={{
              background: "var(--bg-card)",
              padding: "20px",
              borderRadius: "12px",
              border: "1px solid var(--border-color)",
              display: "flex",
              flexDirection: "column",
              gap: "6px"
            }}>
              <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
                Highest Concordance
              </span>
              <div style={{
                fontSize: "32px",
                fontWeight: "bold",
                color: result.overall_similarity > 60 ? "#f87171" : result.overall_similarity > 35 ? "#fbbf24" : "#4ade80"
              }}>
                {result.overall_similarity}%
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Max match with indexed literature
              </span>
            </div>

            {/* Paraphrase Likelihood */}
            <div style={{
              background: "var(--bg-card)",
              padding: "20px",
              borderRadius: "12px",
              border: "1px solid var(--border-color)",
              display: "flex",
              flexDirection: "column",
              gap: "6px"
            }}>
              <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
                Paraphrase Risk
              </span>
              <div style={{
                fontSize: "24px",
                fontWeight: "bold",
                color: result.paraphrase_likelihood === "High" ? "#f87171" : result.paraphrase_likelihood === "Medium" ? "#fbbf24" : "#4ade80"
              }}>
                {result.paraphrase_likelihood} Likelihood
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Semantic reformulation probability
              </span>
            </div>

            {/* Classification Verdict */}
            <div style={{
              background: "var(--bg-card)",
              padding: "20px",
              borderRadius: "12px",
              border: "1px solid var(--border-color)",
              display: "flex",
              flexDirection: "column",
              gap: "6px"
            }}>
              <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
                Authorship Status
              </span>
              <div style={{
                fontSize: "20px",
                fontWeight: "bold",
                color: result.classification === "POTENTIALLY_MANIPULATED" ? "#f87171" : "#4ade80"
              }}>
                {result.classification === "POTENTIALLY_MANIPULATED" ? "⚠️ DERIVATIVE WORK" : "✅ ORIGINAL PROSE"}
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Confidence: {result.confidence}
              </span>
            </div>
          </div>

          {/* Signals */}
          {result.signals && result.signals.length > 0 && (
            <div style={{
              background: "var(--bg-card)",
              padding: "16px 20px",
              borderRadius: "10px",
              border: "1px solid var(--border-color)"
            }}>
              <div style={{ fontSize: "13px", fontWeight: "bold", color: "var(--text-secondary)", marginBottom: "8px" }}>
                🔍 Forensic Evidence Signals:
              </div>
              <ul style={{ margin: 0, paddingLeft: "20px", color: "var(--text-muted)", fontSize: "13px", lineHeight: "1.6" }}>
                {result.signals.map((sig, idx) => (
                  <li key={idx}>{sig}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Matched Passages Breakdown */}
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <h3 style={{ margin: 0, color: "var(--text-primary)", fontSize: "18px" }}>
              Matched Document Sources ({result.matches.length})
            </h3>

            {result.matches.length === 0 ? (
              <div style={{
                background: "var(--bg-card)",
                padding: "24px",
                borderRadius: "10px",
                textAlign: "center",
                color: "#4ade80",
                border: "1px solid rgba(74, 222, 128, 0.2)"
              }}>
                <CheckCircle size={28} style={{ marginBottom: "8px" }} />
                <div>No matching passages found exceeding threshold ({Math.round(threshold * 100)}%). Document is clean.</div>
              </div>
            ) : (
              result.matches.map((match, idx) => {
                const styleInfo = MATCH_TYPE_STYLES[match.match_type] || MATCH_TYPE_STYLES.semantic;
                return (
                  <div key={idx} style={{
                    background: "var(--bg-card)",
                    padding: "20px",
                    borderRadius: "12px",
                    border: "1px solid var(--border-color)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "14px"
                  }}>
                    {/* Match Header */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <span style={{
                          background: "var(--bg-inner)",
                          padding: "4px 8px",
                          borderRadius: "4px",
                          fontSize: "12px",
                          fontWeight: "bold",
                          color: "var(--text-muted)"
                        }}>
                          #{idx + 1}
                        </span>
                        <span style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "15px" }}>
                          {match.source_title}
                        </span>
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <span style={{
                          background: styleInfo.bg,
                          color: styleInfo.color,
                          border: styleInfo.border,
                          padding: "4px 10px",
                          borderRadius: "6px",
                          fontSize: "11px",
                          fontWeight: "bold"
                        }}>
                          {styleInfo.label}
                        </span>
                        <span style={{
                          fontSize: "16px",
                          fontWeight: "bold",
                          color: match.similarity_score > 0.65 ? "#f87171" : "#60a5fa"
                        }}>
                          {Math.round(match.similarity_score * 100)}% Match
                        </span>
                      </div>
                    </div>

                    {/* Side-by-side Passage Inspection */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px" }}>
                      {/* User Text */}
                      <div style={{
                        background: "var(--bg-inner)",
                        padding: "14px",
                        borderRadius: "8px",
                        border: "1px solid var(--border-color)"
                      }}>
                        <div style={{ fontSize: "11px", fontWeight: "bold", color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "6px" }}>
                          Submitted Passage
                        </div>
                        <div style={{ fontSize: "13px", color: "var(--text-primary)", lineHeight: "1.6" }}>
                          "{match.user_passage}"
                        </div>
                      </div>

                      {/* Source Text */}
                      <div style={{
                        background: "var(--bg-inner)",
                        padding: "14px",
                        borderRadius: "8px",
                        border: "1px solid var(--border-color)",
                        borderLeft: `3px solid ${styleInfo.color}`
                      }}>
                        <div style={{ fontSize: "11px", fontWeight: "bold", color: styleInfo.color, textTransform: "uppercase", marginBottom: "6px" }}>
                          Matched Reference Excerpt
                        </div>
                        <div style={{ fontSize: "13px", color: "var(--text-primary)", lineHeight: "1.6" }}>
                          "{match.matched_text}"
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PlagiarismViewer;
