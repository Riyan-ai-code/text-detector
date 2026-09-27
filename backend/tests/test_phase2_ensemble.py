import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from ml.text.ensemble import meta_learner, MetaLearnerEnsemble

client = TestClient(app)

def test_meta_learner_short_vs_long_weights():
    """Verify adaptive length weighting shifts between short snippets and long essays."""
    short_text = "This is a brief text snippet."
    long_text = " ".join(["The quick brown fox jumps over the lazy dog and explores the meadow."] * 30)
    
    res_short = meta_learner.compute_stacked_prediction(
        text=short_text,
        m1_prob=0.8,
        m2_prob=0.8,
        m3_prob=0.8
    )
    res_long = meta_learner.compute_stacked_prediction(
        text=long_text,
        m1_prob=0.8,
        m2_prob=0.8,
        m3_prob=0.8
    )
    
    # In short text, subword/linear components have higher weight than in long text
    assert res_short["weights_used"]["model_3_char_hybrid"] > res_long["weights_used"]["model_3_char_hybrid"]
    # In long text, transformer self-attention dominates
    assert res_long["weights_used"]["model_1_bert"] > res_short["weights_used"]["model_1_bert"]

def test_meta_learner_calibrated_classifications():
    """Verify calibrated probability maps correctly to authentic vs synthetic verdicts."""
    # Strong AI inputs
    ai_res = meta_learner.compute_stacked_prediction(
        text="Furthermore, it is imperative to analyze the profound ramifications of neural paradigms.",
        m1_prob=0.95,
        m2_prob=0.92,
        m3_prob=0.90,
        forensic_features={"metrics": {"burstiness": 20.0, "perplexity": 25.0, "lexical": 30.0}}
    )
    assert ai_res["probability"] >= 0.80
    assert ai_res["classification"] == "AI_GENERATED"
    assert ai_res["confidence"] == "HIGH"
    assert any("cadence" in s or "predictable" in s for s in ai_res["signals"])

    # Strong Human inputs
    human_res = meta_learner.compute_stacked_prediction(
        text="I was walking down by the old bridge yesterday when suddenly my coffee spilled everywhere!",
        m1_prob=0.08,
        m2_prob=0.12,
        m3_prob=0.10,
        forensic_features={"metrics": {"burstiness": 85.0, "perplexity": 75.0, "lexical": 65.0}}
    )
    assert human_res["probability"] <= 0.25
    assert human_res["classification"] == "AUTHENTIC"
    assert human_res["confidence"] == "HIGH"

def test_meta_learner_shap_contributions():
    """Verify SHAP-style component contributions are computed for explainability."""
    res = meta_learner.compute_stacked_prediction(
        text="Testing multi-model ensemble decomposition.",
        m1_prob=0.85,
        m2_prob=0.40,
        m3_prob=0.60
    )
    shap = res["shap_contributions"]
    assert "BERT_Transformer" in shap
    assert "Linear_TFIDF" in shap
    assert "Subword_Char_Hybrid" in shap
    assert "Stylometric_Forensics" in shap
    assert shap["BERT_Transformer"] > 0

def test_text_analysis_endpoint_stacked_ensemble():
    """Verify /api/text/analyze end-to-end integration with Phase 2 Meta-Learner."""
    payload = {
        "text": "Furthermore, neural language models exhibit unprecedented proficiency across various NLP benchmarks.",
        "model": "all",
        "return_sentences": True,
        "return_shap": True
    }
    response = client.post("/api/text/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Common schema checks
    assert "classification" in data
    assert "probability" in data
    assert "confidence" in data
    assert "signals" in data
    assert "analysis_id" in data

    # Phase 2 additions
    assert "model_breakdown" in data
    assert "meta_learner_stacking" in data["model_breakdown"]
    stack_info = data["model_breakdown"]["meta_learner_stacking"]
    assert stack_info["id"] == "meta_learner"
    assert "weights_used" in stack_info

    # SHAP contributions
    assert data["shap_contributions"] is not None
    assert "BERT_Transformer" in data["shap_contributions"]

def test_text_analysis_endpoint_single_model_routing():
    """Verify /api/text/analyze properly honors single-model requests."""
    payload = {
        "text": "The quick brown fox jumps over the lazy dog.",
        "model": "model_2",
        "return_sentences": False,
        "return_shap": True
    }
    response = client.post("/api/text/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] in ["AUTHENTIC", "AI_GENERATED", "AI_ASSISTED", "UNCERTAIN"]
