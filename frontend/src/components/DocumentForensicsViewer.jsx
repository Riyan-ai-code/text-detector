import { useState, useRef } from "react";
import { analyzeDocument } from "../services/api";
import { FileUp, FileText, AlertOctagon, CheckCircle2, ShieldAlert, Cpu, RefreshCw } from "lucide-react";

const SEVERITY_COLORS = {
  HIGH: { bg: "rgba(239, 68, 68, 0.15)", color: "#f87171", border: "1px solid #ef4444" },
  MEDIUM: { bg: "rgba(245, 158, 11, 0.15)", color: "#fbbf24", border: "1px solid #f59e0b" },
  LOW: { bg: "rgba(59, 130, 246, 0.15)", color: "#60a5fa", border: "1px solid #3b82f6" }
};

const DocumentForensicsViewer = ({ onBackToWorkspace }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError("");
    }
  };

  const handleInspect = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const data = await analyzeDocument(file);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err?.message || "Failed to analyze document.");
    } finally {
      setLoading(false);
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
              background: "rgba(245, 158, 11, 0.2)",
              color: "#fbbf24",
              padding: "4px 10px",
              borderRadius: "6px",
              fontSize: "12px",
              fontWeight: "bold",
              letterSpacing: "0.5px"
            }}>
              SYSTEM 3: MULTI-LAYER FORENSICS
            </span>
            <h2 style={{ margin: 0, color: "var(--text-primary)", fontSize: "22px" }}>
              Document Forensics & Typography Anomaly Inspector
            </h2>
          </div>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "14px" }}>
            Deep inspection of PDF / DOCX metadata chronometry, automated compilers, in-paragraph font switches, and zero-width characters.
          </p>
        </div>

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

      {/* Upload Dropzone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        style={{
          background: "var(--bg-card)",
          padding: "36px 24px",
          borderRadius: "12px",
          border: "2px dashed var(--border-color)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "16px",
          textAlign: "center",
          cursor: "pointer",
          transition: "border-color 0.2s"
        }}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt"
          style={{ display: "none" }}
        />

        <div style={{
          width: "56px",
          height: "56px",
          borderRadius: "50%",
          background: "rgba(245, 158, 11, 0.15)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#fbbf24"
        }}>
          <FileUp size={28} />
        </div>

        <div>
          <div style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)", marginBottom: "4px" }}>
            {file ? file.name : "Drag and drop your PDF, DOCX, or TXT file here"}
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-muted)" }}>
            {file ? `${(file.size / 1024).toFixed(1)} KB • Ready to inspect` : "Supports PDF documents, Microsoft Word (.docx), and plain text"}
          </div>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            handleInspect();
          }}
          disabled={!file || loading}
          style={{
            padding: "12px 28px",
            borderRadius: "8px",
            background: "linear-gradient(135deg, #d97706, #f59e0b)",
            color: "#ffffff",
            border: "none",
            fontWeight: "600",
            cursor: !file || loading ? "not-allowed" : "pointer",
            opacity: !file || loading ? 0.5 : 1,
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px",
            marginTop: "8px"
          }}
        >
          {loading ? <RefreshCw size={16} className="spin" /> : <Cpu size={16} />}
          {loading ? "Inspecting File Structure..." : "Run Document Forensics"}
        </button>

        {error && (
          <div style={{ padding: "10px 16px", background: "rgba(239, 68, 68, 0.15)", border: "1px solid #ef4444", borderRadius: "8px", color: "#f87171", fontSize: "13px" }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Results View */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Summary Metric Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
            {/* Risk Classification */}
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
                Authenticity Verdict
              </span>
              <div style={{
                fontSize: "22px",
                fontWeight: "bold",
                color: result.classification === "AUTHENTIC" ? "#4ade80" : "#f87171"
              }}>
                {result.classification === "AUTHENTIC" ? "✅ AUTHENTIC" : "⚠️ " + result.classification}
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Confidence: {result.confidence}
              </span>
            </div>

            {/* Total Structural Anomalies */}
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
                Structural Anomalies
              </span>
              <div style={{
                fontSize: "30px",
                fontWeight: "bold",
                color: result.formatting_anomalies.length > 0 ? "#fbbf24" : "#4ade80"
              }}>
                {result.formatting_anomalies.length} Flagged
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Metadata, font, & layout deviations
              </span>
            </div>

            {/* Citations Audit */}
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
                Citations Audit
              </span>
              <div style={{
                fontSize: "26px",
                fontWeight: "bold",
                color: result.citation_issues.length > 0 ? "#f87171" : "#4ade80"
              }}>
                {result.citations_detected} Found
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                {result.citation_issues.length > 0 ? "⚠️ Missing References Section" : "Verified References Section"}
              </span>
            </div>

            {/* Page Count */}
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
                Document Scope
              </span>
              <div style={{ fontSize: "30px", fontWeight: "bold", color: "var(--text-primary)" }}>
                {result.pages} {result.pages === 1 ? "Page" : "Pages"}
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                File: {result.file_name}
              </span>
            </div>
          </div>

          {/* Metadata Provenance Breakdown */}
          {result.metadata && Object.keys(result.metadata).length > 0 && (
            <div style={{
              background: "var(--bg-card)",
              padding: "20px",
              borderRadius: "12px",
              border: "1px solid var(--border-color)",
              display: "flex",
              flexDirection: "column",
              gap: "14px"
            }}>
              <h3 style={{ margin: 0, color: "var(--text-primary)", fontSize: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                <FileText size={18} color="#fbbf24" /> Metadata Headers & Chronometry Audit
              </h3>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "12px" }}>
                <div style={{ background: "var(--bg-inner)", padding: "12px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>Author Provenance</div>
                  <div style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)" }}>
                    {result.metadata.author || "Unknown"}
                  </div>
                </div>

                <div style={{ background: "var(--bg-inner)", padding: "12px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>Compiler / Producer</div>
                  <div style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)" }}>
                    {result.metadata.producer || result.metadata.creator || "Standard Editor"}
                  </div>
                </div>

                <div style={{ background: "var(--bg-inner)", padding: "12px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>Creation Timestamp</div>
                  <div style={{ fontSize: "13px", color: "var(--text-primary)" }}>
                    {result.metadata.creationDate || result.metadata.created || "Not specified"}
                  </div>
                </div>

                <div style={{ background: "var(--bg-inner)", padding: "12px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>Last Modification</div>
                  <div style={{ fontSize: "13px", color: "var(--text-primary)" }}>
                    {result.metadata.modDate || result.metadata.modified || "Not modified"}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Anomaly Inspection Cards */}
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <h3 style={{ margin: 0, color: "var(--text-primary)", fontSize: "16px" }}>
              Detailed Structural & Typography Anomalies ({result.formatting_anomalies.length})
            </h3>

            {result.formatting_anomalies.length === 0 ? (
              <div style={{
                background: "var(--bg-card)",
                padding: "20px",
                borderRadius: "10px",
                color: "#4ade80",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                border: "1px solid rgba(74, 222, 128, 0.2)"
              }}>
                <CheckCircle2 size={20} />
                <span>No metadata or typography anomalies detected. Document appears genuine.</span>
              </div>
            ) : (
              result.formatting_anomalies.map((anom, idx) => {
                const sevStyle = SEVERITY_COLORS[anom.severity] || SEVERITY_COLORS.LOW;
                return (
                  <div key={idx} style={{
                    background: "var(--bg-card)",
                    padding: "16px 20px",
                    borderRadius: "10px",
                    border: "1px solid var(--border-color)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "16px",
                    flexWrap: "wrap"
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <AlertOctagon size={20} color={sevStyle.color} />
                      <div>
                        <div style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)" }}>
                          {anom.description}
                        </div>
                        <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
                          Category: {anom.type.toUpperCase()} • Page {anom.page || 1}
                        </div>
                      </div>
                    </div>

                    <span style={{
                      background: sevStyle.bg,
                      color: sevStyle.color,
                      border: sevStyle.border,
                      padding: "4px 10px",
                      borderRadius: "6px",
                      fontSize: "11px",
                      fontWeight: "bold"
                    }}>
                      {anom.severity} SEVERITY
                    </span>
                  </div>
                );
              })
            )}
          </div>

          {/* Integrated AI Text Detection Result on Extracted Text */}
          {result.text_analysis && (
            <div style={{
              background: "var(--bg-card)",
              padding: "20px",
              borderRadius: "12px",
              border: "1px solid var(--border-color)",
              display: "flex",
              flexDirection: "column",
              gap: "12px"
            }}>
              <h3 style={{ margin: 0, color: "var(--text-primary)", fontSize: "16px" }}>
                🤖 Integrated Content Text Authenticity
              </h3>
              <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "13px" }}>
                The extracted body text was passed through the multi-model meta-learner stacking engine:
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: "16px", flexWrap: "wrap", marginTop: "4px" }}>
                <span style={{
                  padding: "6px 14px",
                  borderRadius: "6px",
                  background: result.text_analysis.classification.includes("AI") ? "rgba(239, 68, 68, 0.15)" : "rgba(74, 222, 128, 0.15)",
                  color: result.text_analysis.classification.includes("AI") ? "#f87171" : "#4ade80",
                  fontWeight: "bold",
                  fontSize: "13px"
                }}>
                  {result.text_analysis.classification}
                </span>
                <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                  Synthetic Probability: <strong>{Math.round(result.text_analysis.probability * 100)}%</strong>
                </span>
                <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                  Word Count: {result.text_analysis.word_count} • Perplexity: {result.text_analysis.perplexity} • Burstiness: {result.text_analysis.burstiness}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentForensicsViewer;
