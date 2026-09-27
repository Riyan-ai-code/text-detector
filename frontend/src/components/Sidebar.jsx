import {
  FileText,
  Cpu,
  KeyRound,
  ExternalLink,
  Activity,
  TrendingUp
} from "lucide-react";

const Sidebar = ({ selectedModel = "all", setSelectedModel }) => {
  return (
    <div className="sidebar">
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", paddingBottom: "12px" }}>
        <img
          src="https://upload.wikimedia.org/wikipedia/commons/3/32/Cmrit.png"
          width="140"
          height="90"
          alt="CMRIT Logo"
          style={{ objectFit: "contain" }}
        />
      </div>

      <div style={{ fontSize: "11px", fontWeight: "700", color: "#64748b", textTransform: "uppercase", letterSpacing: "1px", margin: "12px 0 6px 12px" }}>
        Core Detection Systems
      </div>

      <ul>
        <li
          className={selectedModel === "all" || selectedModel === "model_1" || selectedModel === "model_2" || selectedModel === "model_3" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("all")}
          style={{ cursor: "pointer" }}
        >
          <FileText size={18} /> ✍️ System 1: AI Text Detector
        </li>

        <li
          className={selectedModel === "plagiarism" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("plagiarism")}
          style={{
            cursor: "pointer",
            background: selectedModel === "plagiarism" ? "rgba(59, 130, 246, 0.2)" : "transparent",
            color: selectedModel === "plagiarism" ? "#60a5fa" : "inherit"
          }}
        >
          <FileText size={18} color="#60a5fa" /> 📑 System 2: Plagiarism & Paraphrase
        </li>

        <li
          className={selectedModel === "documents" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("documents")}
          style={{
            cursor: "pointer",
            background: selectedModel === "documents" ? "rgba(245, 158, 11, 0.2)" : "transparent",
            color: selectedModel === "documents" ? "#fbbf24" : "inherit"
          }}
        >
          <Cpu size={18} color="#fbbf24" /> 📄 System 3: Document Authenticity
        </li>

        <li
          className={selectedModel === "audio" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("audio")}
          style={{
            cursor: "pointer",
            background: selectedModel === "audio" ? "rgba(239, 68, 68, 0.2)" : "transparent",
            color: selectedModel === "audio" ? "#f87171" : "inherit"
          }}
        >
          <Activity size={18} color="#f87171" /> 🎙️ System 4: AI Voice Detector
        </li>

        <div style={{ fontSize: "11px", fontWeight: "700", color: "#64748b", textTransform: "uppercase", letterSpacing: "1px", margin: "16px 0 6px 12px" }}>
          Forensics & Analytics
        </div>

        <li
          className={selectedModel === "forensic" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("forensic")}
          style={{
            cursor: "pointer",
            background: selectedModel === "forensic" ? "rgba(147, 51, 234, 0.2)" : "transparent",
            color: selectedModel === "forensic" ? "#c084fc" : "inherit",
            fontWeight: selectedModel === "forensic" ? "bold" : "normal"
          }}
        >
          <Activity size={18} color="#c084fc" /> 🔬 Forensic Signals Explorer
        </li>

        <li
          className={selectedModel === "model_performance" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("model_performance")}
          style={{
            cursor: "pointer",
            background: selectedModel === "model_performance" ? "rgba(99, 102, 241, 0.2)" : "transparent",
            color: selectedModel === "model_performance" ? "#818cf8" : "inherit",
            fontWeight: selectedModel === "model_performance" ? "bold" : "normal"
          }}
        >
          <TrendingUp size={18} color="#818cf8" /> 📈 Epoch Diagnostics Studio
        </li>

        <li
          className={selectedModel === "writing_profile" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("writing_profile")}
          style={{
            cursor: "pointer",
            background: selectedModel === "writing_profile" ? "rgba(16, 185, 129, 0.2)" : "transparent",
            color: selectedModel === "writing_profile" ? "#34d399" : "inherit",
            fontWeight: selectedModel === "writing_profile" ? "bold" : "normal"
          }}
        >
          <Activity size={18} color="#34d399" /> ✍️ Writing Profile & Baseline
        </li>

        <li
          className={selectedModel === "comparison" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("comparison")}
          style={{
            cursor: "pointer",
            background: selectedModel === "comparison" ? "rgba(56, 189, 248, 0.2)" : "transparent",
            color: selectedModel === "comparison" ? "#38bdf8" : "inherit",
            fontWeight: selectedModel === "comparison" ? "bold" : "normal"
          }}
        >
          <Cpu size={18} color="#38bdf8" /> ⚖️ Document Comparison Mode
        </li>

        <li
          className={selectedModel === "models_info" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("models_info")}
          style={{ cursor: "pointer" }}
        >
          <Cpu size={18} /> Architecture & Models Guide
        </li>

        <div style={{ fontSize: "11px", fontWeight: "700", color: "#64748b", textTransform: "uppercase", letterSpacing: "1px", margin: "20px 0 6px 12px" }}>
          Developer & API
        </div>

        <li
          className={selectedModel === "api" ? "active" : ""}
          onClick={() => setSelectedModel && setSelectedModel("api")}
          style={{
            cursor: "pointer",
            background: selectedModel === "api" ? "rgba(16, 185, 129, 0.2)" : "transparent",
            color: selectedModel === "api" ? "#10b981" : "inherit",
            fontWeight: selectedModel === "api" ? "bold" : "normal"
          }}
        >
          <KeyRound size={18} color="#10b981" /> API Access & Docs
        </li>

        <li>
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            style={{ color: "inherit", textDecoration: "none", display: "flex", alignItems: "center", gap: "10px", width: "100%" }}
          >
            <ExternalLink size={18} /> Swagger REST Docs ↗
          </a>
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;