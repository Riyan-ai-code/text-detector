import { useState } from "react";
import { analyzeText } from "../services/api";
import { Sparkles, Trash2, Clock, FileText } from "lucide-react";

export const PRESET_SAMPLES = [
  {
    id: "chatgpt_essay",
    label: "🤖 ChatGPT-4o Essay",
    text: "Artificial intelligence has revolutionized modern industries by augmenting human capabilities and automating repetitive tasks. Through advanced neural architectures and extensive pretraining on web-scale datasets, large language models exhibit remarkable proficiency across diverse domains including natural language understanding, creative synthesis, and semantic code generation. Furthermore, the integration of deep learning paradigms fosters unprecedented opportunities for accelerated scientific discovery. In essence, this technological revolution serves as a testament to human ingenuity and underscores the importance of ethical governance as we delve into an increasingly automated future."
  },
  {
    id: "claude_technical",
    label: "⚡ Claude 3.5 Spec",
    text: "Distributed database systems require careful trade-offs between consistency, availability, and partition tolerance. When designing consensus algorithms such as Raft or Multi-Paxos, the primary invariant revolves around replicated state machines and term-based leader election. Specifically, log replication guarantees linearizable reads only when quorum leases are strictly enforced. Consequently, engineers must evaluate network latency bounds before configuring heartbeat timeouts and election jitter."
  },
  {
    id: "human_memoir",
    label: "✍️ Human Narrative",
    text: "I spent most of last weekend rummaging through my grandfather's attic, searching for an old wooden toolbox he used to carry everywhere. The air up there smelled like cedar and aged paper, and beneath a stack of dusty canvas tarps, I finally found it. Opening the rusted brass latch brought back a flood of memories—summer afternoons building lopsided birdhouses on the back porch while listening to the hum of cicadas in the maple trees. Dad used to say quality tools outlive their owners, and he wasn't wrong."
  },
  {
    id: "academic_abstract",
    label: "🎓 Academic Paper",
    text: "We present an empirical investigation into stochastic gradient dynamics during transformer fine-tuning across heterogeneous corpora. By analyzing the eigenvalues of the Hessian operator along optimization trajectories, we demonstrate that loss surfaces exhibit anisotropic curvature conditioned on parameter initialization variance. Numerical simulations on benchmark datasets confirm that adaptive learning rates mitigate catastrophic forgetting without sacrificing downstream generalization bounds."
  },
  {
    id: "quillbot_bypassed",
    label: "🛡️ Evasion Sample",
    text: "Artificial\u200b intelligence\u200b has completely transformed\u200b modern enterprise workflows by amplifying worker capabilities. Through cutting-edge neural architectures\u200b and substantial pretraining across web datasets, language algorithms demonstrate outstanding skill across diverse sectors. Additionally, the amalgamation of deep learning models delivers unprecedented avenues for swift scientific exploration and algorithmic refinement."
  },
  {
    id: "mixed_cowritten",
    label: "🤝 50/50 Co-Written",
    text: "In recent years, the acceleration of computational linguistics has reshaped academic discourse across global research institutions. However, I personally found out about this only when my professor caught me fumbling with an old thesis draft last Tuesday. State-of-the-art transformer algorithms demonstrate superior contextual semantic comprehension, yet nothing beats sitting down with a hot cup of black coffee and actually writing notes by hand in a spiral notebook. The machine helps with syntax, but the passion is entirely human."
  }
];

const TextAnalyzer = ({
  text: propText,
  setText: propSetText,
  setResult,
  selectedModel,
  setSelectedModel
}) => {
  const [localText, setLocalText] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const text = propText !== undefined ? propText : localText;
  const setText = propSetText !== undefined ? propSetText : setLocalText;

  const words = text.split(/\s+/).filter(Boolean);
  const wordCount = words.length;
  const charCount = text.length;
  const readTimeSec = Math.ceil((wordCount / 200) * 60);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setErrorMsg("");

    try {
      const res = await analyzeText(text, selectedModel);
      setResult(res);
    } catch (error) {
      console.error(error);
      setErrorMsg("Unable to connect to backend server. Make sure FastAPI server is running on http://127.0.0.1:8000.");
    }

    setLoading(false);
  };

  const handleLoadPreset = (presetText) => {
    setText(presetText);
    setErrorMsg("");
  };

  const handleClear = () => {
    setText("");
    setErrorMsg("");
  };

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
        <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "700" }}>Analysis Workspace</h3>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          style={{
            padding: "6px 12px",
            borderRadius: "6px",
            background: "var(--bg-inner)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-color)",
            fontSize: "13px",
            fontWeight: "500",
            cursor: "pointer"
          }}
        >
          <option value="all">✨ All 3 Models (Blended Ensemble)</option>
          <option value="model_1">🤖 Model 1: BERT Transformer</option>
          <option value="model_2">📊 Model 2: Logistic Regression + SGD</option>
          <option value="model_3">⚡ Model 3: Dual TF-IDF Hybrid Ensemble</option>
        </select>
      </div>

      {/* Preset Pills Bar */}
      <div style={{ display: "flex", gap: "6px", overflowX: "auto", paddingBottom: "4px" }}>
        <span style={{ fontSize: "11px", color: "var(--text-muted)", alignSelf: "center", whiteSpace: "nowrap" }}>
          PRESETS:
        </span>
        {PRESET_SAMPLES.map((sample) => (
          <button
            key={sample.id}
            onClick={() => handleLoadPreset(sample.text)}
            style={{
              padding: "4px 10px",
              borderRadius: "14px",
              background: "var(--bg-inner)",
              color: "var(--text-secondary)",
              border: "1px solid var(--border-color)",
              fontSize: "11px",
              fontWeight: "600",
              cursor: "pointer",
              whiteSpace: "nowrap",
              transition: "all 0.15s"
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#38bdf8")}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border-color)")}
          >
            {sample.label}
          </button>
        ))}
      </div>

      <textarea
        placeholder="Paste or type text sample here, or pick a preset above to run AI detection across all 3 models..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={7}
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

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
        <div style={{ display: "flex", gap: "14px", fontSize: "12px", color: "var(--text-muted)", alignItems: "center" }}>
          <span>
            Words: <strong style={{ color: "var(--text-primary)" }}>{wordCount}</strong>
          </span>
          <span>
            Chars: <strong style={{ color: "var(--text-primary)" }}>{charCount}</strong>
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <Clock size={12} /> ~{readTimeSec}s read
          </span>
          {text && (
            <button
              onClick={handleClear}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "4px",
                background: "transparent",
                border: "none",
                color: "#ef4444",
                cursor: "pointer",
                fontSize: "11px",
                padding: 0
              }}
            >
              <Trash2 size={12} /> Clear
            </button>
          )}
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading || !text.trim()}
          style={{
            padding: "8px 20px",
            borderRadius: "6px",
            background: loading ? "var(--text-muted)" : "var(--accent-gradient)",
            color: "#ffffff",
            fontWeight: "600",
            border: "none",
            cursor: loading ? "not-allowed" : "pointer",
            marginTop: 0
          }}
        >
          {loading ? "Evaluating Models..." : `Analyze (${selectedModel === 'all' ? 'All 3 Models' : selectedModel.toUpperCase()})`}
        </button>
      </div>

      {errorMsg && (
        <div style={{ color: "#ef4444", fontSize: "13px", background: "rgba(239, 68, 68, 0.1)", padding: "8px", borderRadius: "6px" }}>
          {errorMsg}
        </div>
      )}
    </div>
  );
};

export default TextAnalyzer;