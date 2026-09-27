import { useState, useRef } from "react";
import { analyzeAudio } from "../services/api";
import { Mic, Upload, Play, Pause, AlertTriangle, ShieldCheck, Activity, Volume2, RefreshCw } from "lucide-react";

const AudioForensicsViewer = ({ onBackToWorkspace }) => {
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setAudioUrl(URL.createObjectURL(selected));
      setError("");
    }
  };

  const handleInspect = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const data = await analyzeAudio(file);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err?.message || "Failed to analyze audio recording.");
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
              background: "rgba(239, 68, 68, 0.2)",
              color: "#f87171",
              padding: "4px 10px",
              borderRadius: "6px",
              fontSize: "12px",
              fontWeight: "bold",
              letterSpacing: "0.5px"
            }}>
              SYSTEM 4: ACOUSTIC SPECTRAL FORENSICS
            </span>
            <h2 style={{ margin: 0, color: "var(--text-primary)", fontSize: "22px" }}>
              Voice & Audio Synthetic Speech Forensics
            </h2>
          </div>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "14px" }}>
            Acoustic signal processing for pitch micro-tremors, Wiener spectral flatness, 85% roll-off, and neural vocoder artifact detection.
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

      {/* Upload & Audio Preview Card */}
      <div style={{
        background: "var(--bg-card)",
        padding: "28px 24px",
        borderRadius: "12px",
        border: "1px solid var(--border-color)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "16px",
        textAlign: "center"
      }}>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".wav,.mp3,.m4a,.ogg"
          style={{ display: "none" }}
        />

        <div
          onClick={() => fileInputRef.current?.click()}
          style={{
            width: "60px",
            height: "60px",
            borderRadius: "50%",
            background: "rgba(239, 68, 68, 0.15)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#f87171",
            cursor: "pointer"
          }}
        >
          <Mic size={30} />
        </div>

        <div>
          <div style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)", marginBottom: "4px" }}>
            {file ? file.name : "Select an audio recording (WAV, MP3, M4A, OGG)"}
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-muted)" }}>
            {file ? `${(file.size / 1024).toFixed(1)} KB • Ready for acoustic signal processing` : "Supports speech clips, interviews, and voicemail recordings"}
          </div>
        </div>

        {audioUrl && (
          <div style={{ width: "100%", maxWidth: "400px", marginTop: "8px" }}>
            <audio controls src={audioUrl} style={{ width: "100%", borderRadius: "8px" }} />
          </div>
        )}

        <button
          onClick={handleInspect}
          disabled={!file || loading}
          style={{
            padding: "12px 32px",
            borderRadius: "8px",
            background: "linear-gradient(135deg, #dc2626, #ef4444)",
            color: "#ffffff",
            border: "none",
            fontWeight: "600",
            cursor: !file || loading ? "not-allowed" : "pointer",
            opacity: !file || loading ? 0.5 : 1,
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px"
          }}
        >
          {loading ? <RefreshCw size={16} className="spin" /> : <Activity size={16} />}
          {loading ? "Computing Spectral Transforms..." : "Analyze Audio Forensics"}
        </button>

        {error && (
          <div style={{ padding: "10px 16px", background: "rgba(239, 68, 68, 0.15)", border: "1px solid #ef4444", borderRadius: "8px", color: "#f87171", fontSize: "13px" }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Results Panel */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Summary Metric Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
            {/* Authenticity Classification */}
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
                Voice Authenticity
              </span>
              <div style={{
                fontSize: "20px",
                fontWeight: "bold",
                color: result.classification === "AUTHENTIC" ? "#4ade80" : "#f87171"
              }}>
                {result.classification === "AUTHENTIC" ? "✅ HUMAN VOICE" : "⚠️ " + result.classification}
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Confidence: {result.confidence}
              </span>
            </div>

            {/* Synthetic Probability */}
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
                Synthetic Probability
              </span>
              <div style={{
                fontSize: "30px",
                fontWeight: "bold",
                color: result.probability > 0.60 ? "#f87171" : result.probability > 0.35 ? "#fbbf24" : "#4ade80"
              }}>
                {Math.round(result.probability * 100)}%
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Neural vocoder likelihood
              </span>
            </div>

            {/* Recording Scope */}
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
                Signal Duration
              </span>
              <div style={{ fontSize: "28px", fontWeight: "bold", color: "var(--text-primary)" }}>
                {result.duration_seconds}s
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Sample Rate: {result.sample_rate.toLocaleString()} Hz
              </span>
            </div>

            {/* Suspicious Intervals */}
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
                Anomalous Segments
              </span>
              <div style={{
                fontSize: "28px",
                fontWeight: "bold",
                color: result.suspicious_intervals.length > 0 ? "#f87171" : "#4ade80"
              }}>
                {result.suspicious_intervals.length} Flagged
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                0.5s temporal anomaly windows
              </span>
            </div>
          </div>

          {/* Acoustic Forensic Feature Matrix */}
          {result.acoustic_features && (
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
                <Volume2 size={18} color="#f87171" /> Acoustic Spectral Matrix & Micro-Habits
              </h3>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "12px" }}>
                {/* Pitch Stability */}
                <div style={{ background: "var(--bg-inner)", padding: "14px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>Pitch Stability (F0)</div>
                  <div style={{ fontSize: "18px", fontWeight: "bold", color: result.acoustic_features.pitch_stability_f0 > 0.90 ? "#f87171" : "var(--text-primary)", margin: "4px 0" }}>
                    {result.acoustic_features.pitch_stability_f0} / 1.0
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {result.acoustic_features.pitch_stability_f0 > 0.90 ? "⚠️ Unnaturally rigid pitch" : "Natural vocal tremor"}
                  </div>
                </div>

                {/* Spectral Flatness */}
                <div style={{ background: "var(--bg-inner)", padding: "14px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>Wiener Spectral Flatness</div>
                  <div style={{ fontSize: "18px", fontWeight: "bold", color: result.acoustic_features.spectral_flatness > 0.35 ? "#f87171" : "var(--text-primary)", margin: "4px 0" }}>
                    {result.acoustic_features.spectral_flatness}
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {result.acoustic_features.spectral_flatness > 0.35 ? "⚠️ Robotic vocoder noise" : "Organic resonant formants"}
                  </div>
                </div>

                {/* Spectral Roll-off */}
                <div style={{ background: "var(--bg-inner)", padding: "14px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>85% Spectral Roll-Off</div>
                  <div style={{ fontSize: "18px", fontWeight: "bold", color: "var(--text-primary)", margin: "4px 0" }}>
                    {result.acoustic_features.spectral_rolloff_hz} Hz
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    High-frequency energy bound
                  </div>
                </div>

                {/* Zero Crossing Rate */}
                <div style={{ background: "var(--bg-inner)", padding: "14px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>Zero-Crossing Rate (ZCR)</div>
                  <div style={{ fontSize: "18px", fontWeight: "bold", color: "var(--text-primary)", margin: "4px 0" }}>
                    {result.acoustic_features.zero_crossing_rate}
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    Fricative & unvoiced density
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Suspicious Intervals Timeline */}
          <div style={{
            background: "var(--bg-card)",
            padding: "20px",
            borderRadius: "12px",
            border: "1px solid var(--border-color)",
            display: "flex",
            flexDirection: "column",
            gap: "14px"
          }}>
            <h3 style={{ margin: 0, color: "var(--text-primary)", fontSize: "16px" }}>
              ⏱️ Temporal Suspicious Interval Timeline ({result.suspicious_intervals.length})
            </h3>

            {result.suspicious_intervals.length === 0 ? (
              <div style={{
                background: "var(--bg-inner)",
                padding: "16px",
                borderRadius: "8px",
                color: "#4ade80",
                display: "flex",
                alignItems: "center",
                gap: "10px"
              }}>
                <ShieldCheck size={20} />
                <span>No localized neural vocoder phase artifacts detected across the recording timeline.</span>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {result.suspicious_intervals.map((inv, idx) => (
                  <div key={idx} style={{
                    background: "var(--bg-inner)",
                    padding: "12px 16px",
                    borderRadius: "8px",
                    borderLeft: "3px solid #ef4444",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "10px"
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <span style={{
                        background: "rgba(239, 68, 68, 0.2)",
                        color: "#f87171",
                        padding: "3px 8px",
                        borderRadius: "4px",
                        fontSize: "12px",
                        fontWeight: "bold",
                        fontFamily: "monospace"
                      }}>
                        {inv.start_time}s – {inv.end_time}s
                      </span>
                      <span style={{ fontSize: "13px", color: "var(--text-primary)" }}>
                        {inv.reason}
                      </span>
                    </div>

                    <span style={{ fontSize: "12px", fontWeight: "bold", color: "#f87171" }}>
                      Anomaly Score: {Math.round(inv.score * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Forensic Evidence Signals */}
          {result.signals && result.signals.length > 0 && (
            <div style={{
              background: "var(--bg-card)",
              padding: "16px 20px",
              borderRadius: "10px",
              border: "1px solid var(--border-color)"
            }}>
              <div style={{ fontSize: "13px", fontWeight: "bold", color: "var(--text-secondary)", marginBottom: "8px" }}>
                🔍 Acoustic Evidence Signals:
              </div>
              <ul style={{ margin: 0, paddingLeft: "20px", color: "var(--text-muted)", fontSize: "13px", lineHeight: "1.6" }}>
                {result.signals.map((sig, idx) => (
                  <li key={idx}>{sig}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AudioForensicsViewer;
