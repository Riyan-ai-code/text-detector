import axios from "axios";

// Dynamically determine API base URL
const getApiBase = () => {
  if (typeof window !== "undefined" && window.location && window.location.hostname) {
    return `http://${window.location.hostname}:8000`;
  }
  return "http://127.0.0.1:8000";
};

export const API_URL = getApiBase();

// Helper to attempt primary URL then fallback
const requestWithFallback = async (method, path, data = null, isFormData = false) => {
  const primary = `${API_URL}${path}`;
  const fallback = API_URL.includes("localhost") ? `http://127.0.0.1:8000${path}` : `http://localhost:8000${path}`;
  
  const headers = isFormData ? { "Content-Type": "multipart/form-data" } : { "Content-Type": "application/json" };

  try {
    if (method === "GET") {
      const res = await axios.get(primary);
      return res.data;
    }
    const res = await axios.post(primary, data, { headers });
    return res.data;
  } catch (err) {
    if (method === "GET") {
      const res = await axios.get(fallback);
      return res.data;
    }
    const res = await axios.post(fallback, data, { headers });
    return res.data;
  }
};

// System 1: AI Text Detection
export const analyzeText = async (text, model = "all") => {
  return requestWithFallback("POST", "/predict", { text, model });
};

export const analyzeTextUnified = async (text, model = "all", returnSentences = true, returnShap = true) => {
  return requestWithFallback("POST", "/api/text/analyze", {
    text,
    model,
    return_sentences: returnSentences,
    return_shap: returnShap
  });
};

export const extractForensicFeatures = async (text) => {
  return requestWithFallback("POST", "/api/forensic/features", { text });
};

// System 2: Plagiarism & Paraphrase Engine
export const analyzePlagiarism = async (text, threshold = 0.40, topK = 5) => {
  return requestWithFallback("POST", "/api/plagiarism/analyze", {
    text,
    threshold: parseFloat(threshold),
    top_k: parseInt(topK, 10)
  });
};

export const getPlagiarismCorpus = async () => {
  return requestWithFallback("GET", "/api/plagiarism/corpus");
};

// System 3: Document Forensics
export const analyzeDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return requestWithFallback("POST", "/api/documents/analyze", formData, true);
};

// System 4: Voice & Audio Forensics
export const analyzeAudio = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return requestWithFallback("POST", "/api/audio/analyze", formData, true);
};

// System Health
export const getSystemHealth = async () => {
  return requestWithFallback("GET", "/api/health");
};

// Epoch & Model Diagnostics Data System
export const getEpochTrajectory = async () => {
  return requestWithFallback("GET", "/api/model/epochs");
};

export const getEpochSlice = async (epochNum) => {
  return requestWithFallback("GET", `/api/model/epochs/${epochNum}`);
};

export const getModelEvaluation = async () => {
  return requestWithFallback("GET", "/api/model/evaluation");
};

export const getModelCheckpoints = async () => {
  return requestWithFallback("GET", "/api/model/checkpoints");
};

// Data Cleaning & Noise Removal System
export const getDataCleaningStats = async () => {
  return requestWithFallback("GET", "/api/model/data-cleaning/stats");
};

export const getDataCleaningSamples = async () => {
  return requestWithFallback("GET", "/api/model/data-cleaning/samples");
};

export const cleanTextNoise = async (text) => {
  return requestWithFallback("POST", "/api/model/data-cleaning/clean", { text });
};