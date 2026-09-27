import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from ml.plagiarism.semantic_engine import semantic_engine

client = TestClient(app)

def test_semantic_engine_exact_match():
    """Verify verbatim text detection against indexed corpus."""
    exact_text = (
        "The dominant sequence transduction models are based on complex recurrent or "
        "convolutional neural networks that include an encoder and a decoder."
    )
    result = semantic_engine.scan_text(exact_text, threshold=0.5, top_k=3)
    assert len(result["matches"]) > 0
    top_match = result["matches"][0]
    assert top_match["source_id"] == "ref-001"
    assert top_match["match_type"] in ["exact", "near_duplicate"]
    assert top_match["similarity_score"] >= 0.70
    assert result["paraphrase_likelihood"] in ["High", "Medium"]
    assert result["classification"] == "POTENTIALLY_MANIPULATED"

def test_semantic_engine_paraphrase_match():
    """Verify paraphrase and semantic concordance detection with reworded text."""
    paraphrased_text = (
        "We propose replacing the inquiry of whether mechanical computers can think "
        "with an alternative setup framed as an imitation game."
    )
    result = semantic_engine.scan_text(paraphrased_text, threshold=0.30, top_k=3)
    assert len(result["matches"]) > 0
    matched_ids = [m["source_id"] for m in result["matches"]]
    assert "ref-005" in matched_ids  # Turing 1950
    turing_match = next(m for m in result["matches"] if m["source_id"] == "ref-005")
    assert turing_match["similarity_score"] >= 0.35

def test_semantic_engine_novel_authentic_text():
    """Verify completely novel and unrelated text produces clean authentic result."""
    novel_text = (
        "Yesterday evening my younger cousin baked blueberry scones with cinnamon sugar "
        "while we listened to acoustic jazz on an old battery-operated radio."
    )
    result = semantic_engine.scan_text(novel_text, threshold=0.50, top_k=3)
    assert result["overall_similarity"] < 35.0
    assert result["classification"] == "AUTHENTIC"
    assert result["paraphrase_likelihood"] == "Low"

def test_plagiarism_corpus_endpoint():
    """Verify GET /api/plagiarism/corpus returns indexed catalog."""
    response = client.get("/api/plagiarism/corpus")
    assert response.status_code == 200
    corpus = response.json()
    assert isinstance(corpus, list)
    assert len(corpus) >= 8
    titles = [doc["title"] for doc in corpus]
    assert any("Attention Is All You Need" in t for t in titles)
    assert any("BERT" in t for t in titles)
    assert any("Shannon" in t for t in titles)

def test_plagiarism_analyze_endpoint_e2e():
    """Verify POST /api/plagiarism/analyze end-to-end integration."""
    payload = {
        "text": "The fundamental problem of communication is that of reproducing at one point a message selected at another.",
        "threshold": 0.40,
        "top_k": 3
    }
    response = client.post("/api/plagiarism/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "overall_similarity" in data
    assert "matches" in data
    assert len(data["matches"]) > 0
    top_match = data["matches"][0]
    assert "Shannon" in top_match["source_title"] or top_match["source_id"] == "ref-006"
    assert "matched_text" in top_match
    assert "user_passage" in top_match
