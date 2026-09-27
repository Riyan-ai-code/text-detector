import { useState } from "react";
import { extractForensicFeatures } from "../services/api";

const SAMPLE_TEXTS = {
  em_dash_ai: `State-of-the-art neural architectures—specifically modern transformer models—exhibit remarkable contextual agility. Furthermore, the integration of deep attention layers allows for unprecedented linguistic coherence—yet without individual voice. In conclusion, algorithmic synthesis continues to advance exponentially.`,
  human_colloquial: `I walked into my granddad's garage yesterday... smelled just like motor oil and old pine wood! He always said -- never throw away a good rusty wrench (you'll need it later). It made me smile, thinking about all those endless summer afternoons.`
};

const ForensicSignalsView = ({ onBackToWorkspace }) => {
  const [inputText, setInputText] = useState(SAMPLE_TEXTS.em_dash_ai);
  const [features, setFeatures] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleExtract = async (textToAnalyze = inputText) => {
    if (!textToAnalyze.trim()) return;
    setLoading(true);
    setError("");

    try {
      const data = await extractForensicFeatures(textToAnalyze);
      setFeatures(data);
    } catch (err) {
      console.error(err);
      setError(err?.message || "Failed to reach backend API. Make sure python backend is active on port 8000.");
    }
    setLoading(false);
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
        alignItems: "center"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{
              background: "rgba(147, 51, 234, 0.2)",
              color: "#c084fc",
              padding: "4px 10px",
              borderRadius: "6px",
              fontSize: "12px",
              fontWeight: "bold"
            }}>
              RESEARCH STANDARD (PART 1)
            </span>
            <h2 style={{ margin: 0, color: "var(--text-primary)", fontSize: "22px" }}>
              26-Dimension Authorship & Forensic Signals Explorer
            </h2>
          </div>
          <p style={{ margin: "8px 0 0 0", color: "var(--text-muted)", fontSize: "14px" }}>
            Fine-grained computational extraction across punctuation micro-habits, Unicode dashes, entropy, burstiness, and discourse patterns.
          </p>
        </div>
        <button
          onClick={onBackToWorkspace}
          style={{
            padding: "10px 18px",
            borderRadius: "8px",
            background: "var(--accent-gradient)",
            color: "#ffffff",
            border: "none",
            fontWeight: "600",
            cursor: "pointer"
          }}
        >
          ← Single Workspace
        </button>
      </div>

      {/* Input Analysis Box */}
      <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
          <h3 style={{ margin: 0, fontSize: "16px", color: "var(--text-primary)" }}>
            Live Text Input & Signal Extraction
          </h3>
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => {
                setInputText(SAMPLE_TEXTS.em_dash_ai);
                handleExtract(SAMPLE_TEXTS.em_dash_ai);
              }}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                background: "var(--bg-inner)",
                color: "#38bdf8",
                border: "1px solid var(--border-color)",
                fontSize: "12px",
                cursor: "pointer"
              }}
            >
              Load AI Em-Dash Sample
            </button>
            <button
              onClick={() => {
                setInputText(SAMPLE_TEXTS.human_colloquial);
                handleExtract(SAMPLE_TEXTS.human_colloquial);
              }}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                background: "var(--bg-inner)",
                color: "#4ade80",
                border: "1px solid var(--border-color)",
                fontSize: "12px",
                cursor: "pointer"
              }}
            >
              Load Human Colloquial Sample
            </button>
          </div>
        </div>

        <textarea
          rows={5}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste or type text to inspect exact Unicode hyphen/dash metrics, Yule's K, burstiness skewness, and function word ratios..."
          style={{
            width: "100%",
            padding: "12px",
            borderRadius: "8px",
            background: "var(--bg-inner)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-color)",
            fontFamily: "inherit",
            resize: "vertical"
          }}
        />

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "12px" }}>
          <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
            Words: <strong>{inputText.split(/\s+/).filter(Boolean).length}</strong> | Characters: <strong>{inputText.length}</strong>
          </span>
          <button
            onClick={() => handleExtract(inputText)}
            disabled={loading || !inputText.trim()}
            style={{
              padding: "8px 24px",
              borderRadius: "6px",
              background: loading ? "var(--text-muted)" : "var(--accent-gradient)",
              color: "#ffffff",
              fontWeight: "600",
              border: "none",
              cursor: loading ? "not-allowed" : "pointer"
            }}
          >
            {loading ? "Extracting 26 Signals..." : "🔬 Extract Forensic Signals"}
          </button>
        </div>

        {error && (
          <div style={{ color: "#ef4444", fontSize: "13px", background: "rgba(239, 68, 68, 0.1)", padding: "10px", borderRadius: "6px", marginTop: "10px" }}>
            {error}
          </div>
        )}
      </div>

      {/* 4 Multi-Dimensional Forensic Feature Cards */}
      {features && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>
          {/* Card 1: Punctuation & Dash Dissection */}
          <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid #38bdf8" }}>
            <span style={{ fontSize: "12px", color: "#38bdf8", fontWeight: "bold" }}>PART 1 & 2 SIGNAL</span>
            <h3 style={{ margin: "6px 0 14px 0", color: "#38bdf8", fontSize: "18px" }}>Punctuation & Dash Micro-Habits</h3>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Em Dash (— / U+2014) per 1k:</span>
                <strong style={{ color: features.punctuation_and_dashes?.dash_metrics?.em_dash_per_1k > 0 ? "#f87171" : "var(--text-primary)" }}>
                  {features.punctuation_and_dashes?.dash_metrics?.em_dash_per_1k}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Unspaced Em Dash (word—word):</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.punctuation_and_dashes?.dash_metrics?.em_dash_spacing_profile?.["unspaced_count (word—word)"]}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>ASCII Hyphens (-) per 1k:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.punctuation_and_dashes?.dash_metrics?.ascii_hyphen_per_1k}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Hyphenated Compounds:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.punctuation_and_dashes?.dash_metrics?.hyphenated_compounds_count}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Commas per 1k words:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.punctuation_and_dashes?.punctuation_densities_per_1k?.commas}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Punctuation Anomalies (?? / --):</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.punctuation_and_dashes?.punctuation_sequence_anomaly_count}
                </strong>
              </div>
            </div>
          </div>

          {/* Card 2: Structural & Burstiness Distributions */}
          <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid #818cf8" }}>
            <span style={{ fontSize: "12px", color: "#818cf8", fontWeight: "bold" }}>STRUCTURAL DISTRIBUTIONS</span>
            <h3 style={{ margin: "6px 0 14px 0", color: "#818cf8", fontSize: "18px" }}>Sentence & Paragraph Length</h3>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Sentence Count:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.structural_distributions?.sentence_count}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Mean Sentence Length:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.structural_distributions?.sentence_length?.mean_words} words
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Standard Deviation (StdDev):</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.structural_distributions?.sentence_length?.std_deviation}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Burstiness Index (σ/μ):</span>
                <strong style={{ color: features.structural_distributions?.sentence_length?.burstiness_index < 25 ? "#f87171" : "#4ade80" }}>
                  {features.structural_distributions?.sentence_length?.burstiness_index}%
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Sentence Length Range:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.structural_distributions?.sentence_length?.min_words} – {features.structural_distributions?.sentence_length?.max_words} words
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Length Skewness (Asymmetry):</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.structural_distributions?.sentence_length?.length_skewness}
                </strong>
              </div>
            </div>
          </div>

          {/* Card 3: Lexical Information & Entropy */}
          <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid #c084fc" }}>
            <span style={{ fontSize: "12px", color: "#c084fc", fontWeight: "bold" }}>INFORMATION THEORY</span>
            <h3 style={{ margin: "6px 0 14px 0", color: "#c084fc", fontSize: "18px" }}>Lexical Richness & Entropy</h3>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Type-Token Ratio (TTR):</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.lexical_information?.vocabulary_diversity_ttr}%
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Hapax Legomena Ratio:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.lexical_information?.hapax_legomena_ratio}%
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Yule's Characteristic K:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.lexical_information?.yules_characteristic_k}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Shannon Lexical Entropy:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.lexical_information?.shannon_lexical_entropy} bits
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>ALL-CAPS Density:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.surface_and_formatting?.all_caps_word_density_pct}%
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Title Case Ratio:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.surface_and_formatting?.title_cased_word_ratio_pct}%
                </strong>
              </div>
            </div>
          </div>

          {/* Card 4: Syntax & Discourse Patterns */}
          <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid #10b981" }}>
            <span style={{ fontSize: "12px", color: "#10b981", fontWeight: "bold" }}>DISCOURSE & SYNTAX</span>
            <h3 style={{ margin: "6px 0 14px 0", color: "#10b981", fontSize: "18px" }}>Function Words & Transitions</h3>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Function Word Ratio:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.syntax_and_discourse?.function_word_ratio_pct}%
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Discourse Transitions / 1k:</span>
                <strong style={{ color: features.syntax_and_discourse?.discourse_transitions_per_1k > 40 ? "#f87171" : "var(--text-primary)" }}>
                  {features.syntax_and_discourse?.discourse_transitions_per_1k}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Phrase Reuse (Trigram %):</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.syntax_and_discourse?.phrase_reuse_trigram_pct}%
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Trailing Whitespace:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.surface_and_formatting?.has_trailing_whitespace ? "Detected" : "Clean"}
                </strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Total Analyzed Characters:</span>
                <strong style={{ color: "var(--text-primary)" }}>
                  {features.summary?.total_chars}
                </strong>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ForensicSignalsView;
