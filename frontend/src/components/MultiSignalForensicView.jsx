import React, { useState } from "react";
import {
  Activity,
  Layers,
  Fingerprint,
  BarChart2,
  TrendingUp,
  Sliders,
  Type,
  AlignLeft,
  PieChart,
  HelpCircle,
  Cpu
} from "lucide-react";

const MultiSignalForensicView = ({ result }) => {
  const [activeTab, setActiveTab] = useState("statistical");

  if (!result) return null;

  const stat = result.statistical_signals || {};
  const stylo = result.stylometric_signals || {};
  const fp = result.fingerprint_signals || {};
  const calib = result.calibration || {};

  const modelFamily = fp.model_family_hypothesis || {
    category: "Other / Unknown",
    confidence: "Low",
    probability: 0.35,
    explanation: "Signals heterogeneous.",
    disclaimer: "Heuristic estimation only."
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
      {/* Header & Signal Sub-Tabs */}
      <div
        style={{
          padding: "16px 20px",
          borderBottom: "1px solid var(--border-color)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px"
        }}
      >
        <div>
          <h3 style={{ margin: "0 0 4px 0", fontSize: "17px", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
            <Activity size={18} color="#38bdf8" />
            Multi-Signal Forensic Decomposition
          </h3>
          <p style={{ margin: 0, fontSize: "12px", color: "var(--text-muted)" }}>
            Independent statistical, stylometric, and model fingerprint signals evaluated in parallel
          </p>
        </div>

        {/* Signal Navigation Pills */}
        <div style={{ display: "flex", gap: "6px", background: "var(--bg-inner)", padding: "4px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <button
            onClick={() => setActiveTab("statistical")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "none",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: activeTab === "statistical" ? "var(--accent-blue)" : "transparent",
              color: activeTab === "statistical" ? "#fff" : "var(--text-secondary)",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <BarChart2 size={14} /> Statistical Signals
          </button>
          <button
            onClick={() => setActiveTab("stylometric")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "none",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: activeTab === "stylometric" ? "var(--accent-blue)" : "transparent",
              color: activeTab === "stylometric" ? "#fff" : "var(--text-secondary)",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <Layers size={14} /> Stylometric Signals
          </button>
          <button
            onClick={() => setActiveTab("fingerprint")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "none",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: activeTab === "fingerprint" ? "var(--accent-blue)" : "transparent",
              color: activeTab === "fingerprint" ? "#fff" : "var(--text-secondary)",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <Fingerprint size={14} /> AI Fingerprint & Family
          </button>
          <button
            onClick={() => setActiveTab("watermark")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "none",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              background: activeTab === "watermark" ? "var(--accent-blue)" : "transparent",
              color: activeTab === "watermark" ? "#fff" : "var(--text-secondary)",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <Sliders size={14} /> Watermark & Paraphrase
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div style={{ padding: "20px" }}>
        {/* 1. STATISTICAL SIGNALS TAB */}
        {activeTab === "statistical" && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
            {/* Perplexity & Predictability */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>INFORMATION THEORY</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#38bdf8", fontSize: "15px" }}>Perplexity & Predictability</h4>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", fontSize: "13px" }}>
                <span>Predictability Index:</span>
                <strong style={{ color: stat.perplexity?.predictability_score > 65 ? "#f87171" : "#4ade80" }}>
                  {stat.perplexity?.predictability_score || 50}%
                </strong>
              </div>
              <div style={{ width: "100%", height: "8px", background: "var(--bg-card)", borderRadius: "4px", overflow: "hidden", marginBottom: "12px" }}>
                <div
                  style={{
                    width: `${stat.perplexity?.predictability_score || 50}%`,
                    height: "100%",
                    background: stat.perplexity?.predictability_score > 65 ? "#f87171" : "#38bdf8"
                  }}
                />
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <div>Estimated Perplexity: <strong>{stat.perplexity?.estimated_perplexity || "N/A"}</strong></div>
                <div>Vocabulary Entropy (Shannon): <strong>{stat.perplexity?.shannon_entropy || "N/A"} bits</strong></div>
                <div>Character Entropy: <strong>{stat.perplexity?.character_entropy || "N/A"}</strong></div>
              </div>
            </div>

            {/* Burstiness & Length Distributions */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>SENTENCE DISTRIBUTIONS</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#818cf8", fontSize: "15px" }}>Burstiness & Sentence Lengths</h4>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", fontSize: "13px" }}>
                <span>Burstiness Score:</span>
                <strong style={{ color: stat.burstiness?.burstiness_index < 35 ? "#f87171" : "#4ade80" }}>
                  {stat.burstiness?.burstiness_index || 50} / 100
                </strong>
              </div>
              <p style={{ margin: "0 0 8px 0", fontSize: "11px", color: "var(--text-muted)" }}>
                {stat.burstiness?.burstiness_index < 35
                  ? "⚠️ Highly uniform sentence lengths characteristic of synthetic generators."
                  : "✓ Natural cadence variation typical of human composition."}
              </p>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <div>Mean Sentence Length: <strong>{stat.burstiness?.mean_sentence_length || 0} words</strong></div>
                <div>Std Deviation: <strong>±{stat.burstiness?.std_sentence_length || 0} words</strong></div>
                <div>Range: <strong>{stat.sentence_length_distribution?.min || 0} to {stat.sentence_length_distribution?.max || 0} words</strong></div>
              </div>
            </div>

            {/* Vocabulary Diversity & N-gram Repetition */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>LEXICAL METRICS</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#c084fc", fontSize: "15px" }}>Vocabulary Diversity & Repetition</h4>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "6px" }}>
                <div>Type-Token Ratio (TTR): <strong>{stat.vocabulary_diversity?.type_token_ratio || 0}</strong></div>
                <div>Simpson's Diversity Index (D): <strong>{stat.vocabulary_diversity?.simpsons_diversity_index || 0}</strong></div>
                <div>Bigram Repetition Rate: <strong>{stat.ngram_repetitions?.bigram_repeat_rate_pct || 0}%</strong></div>
                <div>Trigram Repetition Rate: <strong>{stat.ngram_repetitions?.trigram_repeat_rate_pct || 0}%</strong></div>
              </div>

              {stat.ngram_repetitions?.repeated_phrases?.length > 0 && (
                <div style={{ marginTop: "10px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>REPEATED 3-GRAMS:</span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                    {stat.ngram_repetitions.repeated_phrases.map((p, idx) => (
                      <span key={idx} style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", padding: "2px 6px", borderRadius: "4px", fontSize: "11px" }}>
                        "{p.phrase}" (×{p.count})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Punctuation Profile */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>PUNCTUATION DISSECTION</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#34d399", fontSize: "15px" }}>Punctuation Density</h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "12px", color: "var(--text-secondary)" }}>
                <div>Commas: <strong>{stat.punctuation_distribution?.counts?.comma || 0}</strong></div>
                <div>Semicolons: <strong>{stat.punctuation_distribution?.counts?.semicolon || 0}</strong></div>
                <div>Colons: <strong>{stat.punctuation_distribution?.counts?.colon || 0}</strong></div>
                <div>Em-dashes: <strong>{stat.punctuation_distribution?.counts?.em_dash || 0}</strong></div>
                <div>Parentheses: <strong>{stat.punctuation_distribution?.counts?.parentheses || 0}</strong></div>
                <div>Quotes: <strong>{stat.punctuation_distribution?.counts?.quotes || 0}</strong></div>
              </div>
              <div style={{ marginTop: "10px", fontSize: "11px", color: "var(--text-muted)" }}>
                Punctuation Ratio: <strong>{stat.punctuation_distribution?.punctuation_to_word_ratio || 0} marks/word</strong>
              </div>
            </div>
          </div>
        )}

        {/* 2. STYLOMETRIC SIGNALS TAB */}
        {activeTab === "stylometric" && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
            {/* Active vs Passive Voice */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>SYNTACTIC VOICE</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#38bdf8", fontSize: "15px" }}>Active vs. Passive Voice</h4>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", fontSize: "13px" }}>
                <span>Active: <strong>{stylo.voice_distribution?.active_percentage || 100}%</strong></span>
                <span>Passive: <strong>{stylo.voice_distribution?.passive_percentage || 0}%</strong></span>
              </div>
              <div style={{ width: "100%", height: "10px", background: "var(--bg-card)", borderRadius: "5px", overflow: "hidden", display: "flex", marginBottom: "10px" }}>
                <div style={{ width: `${stylo.voice_distribution?.active_percentage || 100}%`, height: "100%", background: "#34d399" }} />
                <div style={{ width: `${stylo.voice_distribution?.passive_percentage || 0}%`, height: "100%", background: "#f59e0b" }} />
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                Dominant Voice: <strong style={{ color: "#38bdf8" }}>{stylo.voice_distribution?.dominant_voice || "Active"}</strong>
                <p style={{ margin: "4px 0 0 0", fontSize: "11px", color: "var(--text-muted)" }}>
                  {stylo.voice_distribution?.passive_percentage > 40
                    ? "Elevated passive construction typical of formal academic or synthetic technical writing."
                    : "Direct active voice dominant."}
                </p>
              </div>
            </div>

            {/* Discourse Transitions */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>DISCOURSE MARKERS</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#f59e0b", fontSize: "15px" }}>Formal Transitions</h4>
              <div style={{ fontSize: "13px", marginBottom: "8px" }}>
                Transition Density: <strong>{stylo.discourse_transitions?.transition_density_per_100_words || 0} per 100 words</strong>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {stylo.discourse_transitions?.markers_detected?.length > 0 ? (
                  stylo.discourse_transitions.markers_detected.map((m, idx) => (
                    <span key={idx} style={{ background: "rgba(245, 158, 11, 0.15)", color: "#fbbf24", padding: "2px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "600" }}>
                      {m.marker} (×{m.count})
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>No formal transitional markers detected.</span>
                )}
              </div>
            </div>

            {/* Pronoun & Perspective Distribution */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>AUTHORIAL STANCE</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#c084fc", fontSize: "15px" }}>Pronouns & Perspective</h4>
              <div style={{ fontSize: "13px", fontWeight: "700", color: "#c084fc", marginBottom: "8px" }}>
                {stylo.pronoun_usage?.perspective || "Impersonal / Third-Person Objective"}
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <div>1st Person (I, we): <strong>{stylo.pronoun_usage?.first_person_pct || 0}%</strong></div>
                <div>2nd Person (you): <strong>{stylo.pronoun_usage?.second_person_pct || 0}%</strong></div>
                <div>3rd Person (he, she, they, it): <strong>{stylo.pronoun_usage?.third_person_pct || 0}%</strong></div>
                <div>Impersonal Ratio: <strong>{stylo.pronoun_usage?.impersonal_ratio_pct || 50}%</strong></div>
              </div>
            </div>

            {/* Sentence Complexity & Clauses */}
            <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>SYNTACTIC COMPLEXITY</span>
              <h4 style={{ margin: "4px 0 12px 0", color: "#34d399", fontSize: "15px" }}>Clause Depth & Subordination</h4>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "6px" }}>
                <div>Complexity Tier: <strong style={{ color: "#34d399" }}>{stylo.sentence_complexity?.complexity_level || "Simple"}</strong></div>
                <div>Avg Clauses / Sentence: <strong>{stylo.sentence_complexity?.average_clauses_per_sentence || 1}</strong></div>
                <div>Subordinate Conjunctions: <strong>{stylo.sentence_complexity?.subordinate_conjunctions_count || 0}</strong></div>
                <div>Paragraph Uniformity: <strong>{stylo.paragraph_structure?.uniformity_score || 50} / 100</strong></div>
              </div>
            </div>
          </div>
        )}

        {/* 3. AI FINGERPRINT & MODEL FAMILY TAB */}
        {activeTab === "fingerprint" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Model Family Hypothesis Card */}
            <div
              style={{
                background: "linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(147, 51, 234, 0.08))",
                border: "1.5px solid rgba(147, 51, 234, 0.4)",
                borderRadius: "10px",
                padding: "16px 20px"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px", marginBottom: "8px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Cpu size={20} color="#c084fc" />
                  <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "700" }}>MODEL FAMILY ATTRIBUTION HYPOTHESIS</span>
                </div>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  <span style={{ background: "rgba(147, 51, 234, 0.2)", color: "#c084fc", padding: "4px 10px", borderRadius: "6px", fontSize: "13px", fontWeight: "700" }}>
                    {modelFamily.category}
                  </span>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    Confidence: <strong>{modelFamily.confidence}</strong> ({Math.round(modelFamily.probability * 100)}%)
                  </span>
                </div>
              </div>

              <p style={{ margin: "0 0 10px 0", fontSize: "14px", color: "var(--text-primary)", lineHeight: "1.5" }}>
                {modelFamily.explanation}
              </p>

              <div style={{ background: "var(--bg-card)", padding: "10px 14px", borderRadius: "6px", fontSize: "12px", color: "var(--text-muted)", fontStyle: "italic", border: "1px solid var(--border-color)" }}>
                ⚠️ <strong>Important Uncertainty Disclaimer:</strong> {modelFamily.disclaimer}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
              {/* Cliché Detection */}
              <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>SYNTHETIC TRANSITION IDIOMS</span>
                <h4 style={{ margin: "4px 0 12px 0", color: "#f87171", fontSize: "15px" }}>LLM Cliché Catalog</h4>
                <div style={{ fontSize: "13px", marginBottom: "8px" }}>
                  Total Clichés: <strong style={{ color: fp.cliche_analysis?.total_cliches_detected > 0 ? "#f87171" : "#4ade80" }}>
                    {fp.cliche_analysis?.total_cliches_detected || 0}
                  </strong>
                  {" • "}Density: <strong>{fp.cliche_analysis?.cliche_density_pct || 0}%</strong>
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {fp.cliche_analysis?.detected_phrases?.length > 0 ? (
                    fp.cliche_analysis.detected_phrases.map((c, idx) => (
                      <span key={idx} style={{ background: "rgba(239, 68, 68, 0.15)", color: "#fca5a5", padding: "3px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "600" }}>
                        "{c.cliche}" (×{c.occurrences})
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>No formulaic LLM clichés identified.</span>
                  )}
                </div>
              </div>

              {/* Sentence Openings & Semantic Redundancy */}
              <div style={{ background: "var(--bg-inner)", padding: "16px", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>STRUCTURAL MONOTONY</span>
                <h4 style={{ margin: "4px 0 12px 0", color: "#38bdf8", fontSize: "15px" }}>Sentence Openings & Redundancy</h4>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "6px" }}>
                  <div>Opening Monotony: <strong>{fp.sentence_openings?.monotony_score || 0} / 100</strong></div>
                  <div>Dominant Opening: <strong>{fp.sentence_openings?.dominant_opening_type || "Variable"}</strong></div>
                  <div>Semantic Redundancy: <strong>{fp.semantic_redundancy?.redundancy_score || 0} / 100</strong></div>
                  <div>Content Overlap: <strong>{fp.semantic_redundancy?.is_redundant ? "Repetitive Concepts Detected" : "Low Semantic Overlap"}</strong></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 4. WATERMARK & PARAPHRASE TAB (EXPERIMENTAL) */}
        {activeTab === "watermark" && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
            {/* Watermark Analysis */}
            <div style={{ background: "var(--bg-inner)", padding: "20px", borderRadius: "10px", border: "1px solid var(--border-color)", display: "flex", flexDirection: "column", gap: "12px" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "700" }}>EXPERIMENTAL MODULE</span>
              <h4 style={{ margin: 0, color: "#38bdf8", fontSize: "16px" }}>Statistical AI Watermark Analysis</h4>
              
              <div style={{ background: "var(--bg-card)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
                <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>STATUS:</div>
                <div style={{ fontSize: "14px", fontWeight: "700", color: result.watermark_analysis?.watermark_detected ? "#f87171" : "#4ade80" }}>
                  {result.watermark_analysis?.status || "No reliable watermark detected"}
                </div>
              </div>

              <div style={{ fontSize: "13px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "6px" }}>
                <div>Statistical Z-Score: <strong>{result.watermark_analysis?.z_score ?? 0.0}</strong></div>
                <div>Green-list Token Ratio: <strong>{result.watermark_analysis?.green_list_ratio ?? 50.0}%</strong></div>
                <div>Tokens Evaluated: <strong>{result.watermark_analysis?.tokens_evaluated ?? 0}</strong></div>
              </div>

              <div style={{ background: "rgba(56, 189, 248, 0.08)", borderLeft: "3px solid #38bdf8", padding: "10px", borderRadius: "4px", fontSize: "12px", color: "var(--text-secondary)" }}>
                📌 <strong>Note:</strong> {result.watermark_analysis?.note || "Absence of a watermark does not establish human authorship."}
              </div>

              <div style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic" }}>
                {result.watermark_analysis?.disclaimer || "Do not claim to detect proprietary or unknown watermarks without evidence."}
              </div>
            </div>

            {/* AI Paraphrasing Detection */}
            <div style={{ background: "var(--bg-inner)", padding: "20px", borderRadius: "10px", border: "1px solid var(--border-color)", display: "flex", flexDirection: "column", gap: "12px" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "700" }}>EXPERIMENTAL MODULE</span>
              <h4 style={{ margin: 0, color: "#c084fc", fontSize: "16px" }}>AI Paraphrasing & Spin Detection</h4>

              <div style={{ background: "var(--bg-card)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
                <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>PARAPHRASE RISK:</div>
                <div style={{ fontSize: "14px", fontWeight: "700", color: result.paraphrase_analysis?.is_paraphrased_detected ? "#f87171" : "#4ade80" }}>
                  {result.paraphrase_analysis?.status || "No Spin Artifacts"} ({result.paraphrase_analysis?.paraphrase_risk_score ?? 0}/100)
                </div>
              </div>

              <p style={{ margin: 0, fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                {result.paraphrase_analysis?.explanation || "Scans for unnatural synonym substitutions combined with preserved syntactic frameworks typical of QuillBot or spinning algorithms."}
              </p>

              {result.paraphrase_analysis?.detected_spin_markers?.length > 0 && (
                <div>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>SPIN ARTIFACTS:</span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {result.paraphrase_analysis.detected_spin_markers.map((m, idx) => (
                      <span key={idx} style={{ background: "rgba(239, 68, 68, 0.15)", color: "#fca5a5", padding: "2px 8px", borderRadius: "4px", fontSize: "11px" }}>
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic", marginTop: "auto" }}>
                {result.paraphrase_analysis?.disclaimer || "AI Paraphrase Detection is an experimental module."}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiSignalForensicView;
