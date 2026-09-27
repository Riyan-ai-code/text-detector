import React, { useState, useEffect } from "react";
import axios from "axios";
import { UserCheck, Sliders, AlertTriangle, CheckCircle, BookOpen, RefreshCw, Upload } from "lucide-react";
import { API_URL } from "../services/api";

const WritingProfileBaseline = ({ currentText, onBackToWorkspace }) => {
  const [baseline, setBaseline] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [comparing, setComparing] = useState(false);
  const [samples, setSamples] = useState(["", "", ""]);
  const [isEditingBaseline, setIsEditingBaseline] = useState(false);
  const [profileName, setProfileName] = useState("My Genuine Writing Profile");

  // Load default baseline on mount
  useEffect(() => {
    fetchDefaultBaseline();
  }, []);

  // When currentText or baseline changes, run comparison
  useEffect(() => {
    if (baseline && currentText && currentText.trim().length >= 20) {
      runComparison(currentText, baseline);
    }
  }, [baseline, currentText]);

  const fetchDefaultBaseline = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/api/baseline/default`);
      setBaseline(res.data);
    } catch (e) {
      console.error("Failed to load default baseline", e);
    }
    setLoading(false);
  };

  const runComparison = async (text, activeBaseline) => {
    setComparing(true);
    try {
      const res = await axios.post(`${API_URL}/api/baseline/compare`, {
        text,
        baseline: activeBaseline
      });
      setComparison(res.data);
    } catch (e) {
      console.error("Comparison failed", e);
    }
    setComparing(false);
  };

  const handleCreateCustomBaseline = async () => {
    const valid = samples.filter(s => s.trim().length >= 30);
    if (valid.length < 1) {
      alert("Please provide at least 1-3 genuine writing samples (minimum 30 characters each).");
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/baseline/create`, {
        samples: valid,
        profile_name: profileName
      });
      setBaseline(res.data);
      setIsEditingBaseline(false);
      if (currentText && currentText.trim()) {
        runComparison(currentText, res.data);
      }
    } catch (e) {
      console.error("Failed to create baseline", e);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Top Banner */}
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
            <UserCheck size={22} color="#10b981" />
            Personal Writing Fingerprint Baseline
          </h2>
          <p style={{ margin: 0, fontSize: "14px", color: "var(--text-muted)" }}>
            Calibrate detection against your genuine personal writing style. Distinguishes authentic idiosyncratic habits from AI-generated prose.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={() => setIsEditingBaseline(!isEditingBaseline)}
            style={{
              padding: "8px 14px",
              borderRadius: "6px",
              background: "var(--bg-inner)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-color)",
              fontSize: "13px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <Sliders size={14} />
            {isEditingBaseline ? "Close Sample Editor" : "Train Custom Baseline (3–5 Samples)"}
          </button>
          {onBackToWorkspace && (
            <button
              onClick={onBackToWorkspace}
              style={{
                padding: "8px 16px",
                borderRadius: "6px",
                background: "var(--accent-gradient)",
                color: "#fff",
                border: "none",
                fontSize: "13px",
                fontWeight: "600",
                cursor: "pointer"
              }}
            >
              ← Back to Workspace
            </button>
          )}
        </div>
      </div>

      {/* Sample Editor Drawer (when expanded) */}
      {isEditingBaseline && (
        <div
          style={{
            background: "var(--bg-card)",
            padding: "20px",
            borderRadius: "12px",
            border: "1.5px solid #10b981"
          }}
        >
          <h3 style={{ margin: "0 0 6px 0", fontSize: "16px", color: "#34d399" }}>
            Upload or Paste 3–5 Genuine Writing Samples
          </h3>
          <p style={{ margin: "0 0 16px 0", fontSize: "13px", color: "var(--text-muted)" }}>
            These samples must be 100% human-authored essays, emails, journal entries, or papers representing your natural voice.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginBottom: "16px" }}>
            {samples.map((s, idx) => (
              <div key={idx}>
                <label style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                  Genuine Writing Sample #{idx + 1}
                </label>
                <textarea
                  value={s}
                  onChange={(e) => {
                    const next = [...samples];
                    next[idx] = e.target.value;
                    setSamples(next);
                  }}
                  placeholder={`Paste sample #${idx + 1} here (e.g. personal essay, email, or article)...`}
                  rows={4}
                  style={{
                    width: "100%",
                    padding: "10px",
                    borderRadius: "6px",
                    background: "var(--bg-inner)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    fontSize: "13px",
                    fontFamily: "inherit",
                    resize: "vertical"
                  }}
                />
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <button
              onClick={() => setSamples([...samples, ""])}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                background: "var(--bg-inner)",
                color: "var(--text-secondary)",
                border: "1px solid var(--border-color)",
                fontSize: "12px",
                cursor: "pointer"
              }}
            >
              + Add Another Sample (Up to 5)
            </button>
            <button
              onClick={handleCreateCustomBaseline}
              disabled={loading}
              style={{
                padding: "8px 18px",
                borderRadius: "6px",
                background: "#10b981",
                color: "#fff",
                border: "none",
                fontSize: "13px",
                fontWeight: "700",
                cursor: "pointer"
              }}
            >
              {loading ? "Computing Fingerprint..." : "Compute & Save Personal Baseline"}
            </button>
          </div>
        </div>
      )}

      {/* Comparison Results Area */}
      {comparison && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
          {/* Similarity & Deviation Card */}
          <div
            style={{
              background: "var(--bg-card)",
              padding: "24px",
              borderRadius: "12px",
              border: "1px solid var(--border-color)",
              display: "flex",
              flexDirection: "column",
              gap: "20px"
            }}
          >
            <div>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "700" }}>
                ACTIVE PROFILE: {comparison.profile_name}
              </span>
              <h3 style={{ margin: "4px 0 16px 0", fontSize: "18px", color: "var(--text-primary)" }}>
                Authorial Fingerprint Match
              </h3>

              {/* Similarity Bar */}
              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
                  <span style={{ fontWeight: "600", color: "var(--text-primary)" }}>Similarity to your writing style</span>
                  <strong style={{ color: "#34d399", fontSize: "15px" }}>{comparison.style_similarity_pct}%</strong>
                </div>
                <div style={{ fontFamily: "monospace", fontSize: "18px", letterSpacing: "2px", color: "#34d399" }}>
                  {comparison.similarity_bar}
                </div>
              </div>

              {/* Style Deviation Bar */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
                  <span style={{ fontWeight: "600", color: "var(--text-primary)" }}>Style deviation</span>
                  <strong style={{ color: comparison.style_deviation_pct > 40 ? "#f87171" : "#fbbf24", fontSize: "15px" }}>
                    {comparison.style_deviation_pct}%
                  </strong>
                </div>
                <div style={{ fontFamily: "monospace", fontSize: "18px", letterSpacing: "2px", color: comparison.style_deviation_pct > 40 ? "#f87171" : "#fbbf24" }}>
                  {comparison.deviation_bar}
                </div>
              </div>
            </div>

            {/* Shift Explanations */}
            <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "16px" }}>
              <h4 style={{ margin: "0 0 10px 0", fontSize: "14px", color: "var(--text-primary)" }}>
                Characteristics Shifts Explained:
              </h4>
              <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {comparison.shift_explanations.map((exp, idx) => (
                  <li key={idx}>{exp}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Dimensional Comparisons Table */}
          <div
            style={{
              background: "var(--bg-card)",
              padding: "24px",
              borderRadius: "12px",
              border: "1px solid var(--border-color)"
            }}
          >
            <h3 style={{ margin: "0 0 14px 0", fontSize: "17px", color: "var(--text-primary)" }}>
              Baseline vs. Target Document Dimensions
            </h3>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-color)", textAlign: "left", color: "var(--text-muted)" }}>
                    <th style={{ padding: "8px 6px" }}>Stylistic Dimension</th>
                    <th style={{ padding: "8px 6px" }}>Your Baseline</th>
                    <th style={{ padding: "8px 6px" }}>Target Text</th>
                    <th style={{ padding: "8px 6px" }}>Deviation</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.dimension_comparisons.map((row, idx) => (
                    <tr key={idx} style={{ borderBottom: "1px solid var(--border-color)" }}>
                      <td style={{ padding: "10px 6px", fontWeight: "500", color: "var(--text-primary)" }}>
                        {row.dimension}
                      </td>
                      <td style={{ padding: "10px 6px", color: "#38bdf8" }}>{row.baseline_val}</td>
                      <td style={{ padding: "10px 6px", color: "var(--text-secondary)" }}>{row.current_val}</td>
                      <td style={{ padding: "10px 6px", fontWeight: "600", color: row.deviation.includes("+") ? "#f87171" : "#34d399" }}>
                        {row.deviation}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ marginTop: "14px", fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic" }}>
              💡 Dimensions deviating significantly from your baseline indicate possible ghostwriting, AI assistance, or stylistic divergence.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WritingProfileBaseline;
