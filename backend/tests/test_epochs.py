import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from ml.text.data_cleaner import data_cleaner

client = TestClient(app)


def test_get_10_epoch_trajectory():
    response = client.get("/api/model/epochs")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_epochs"] == 10
    assert data["max_steps"] == 5000
    assert len(data["epochs"]) == 10
    
    # Verify Epoch 6 is the optimal generalization checkpoint (global min val loss: 0.0185)
    ep6 = next(e for e in data["epochs"] if round(e["epoch"]) == 6)
    assert ep6["is_best"] is True
    assert ep6["eval_loss"] == 0.0185
    assert ep6["accuracy"] == 99.75
    assert ep6["f1_score"] == 99.75
    
    # Verify step loss history with EMA noise smoothing
    assert "step_loss_history" in data
    assert len(data["step_loss_history"]) > 0
    first_step = data["step_loss_history"][0]
    assert "smoothed_loss" in first_step
    assert "raw_loss" in first_step
    assert "learning_rate" in first_step


def test_get_single_epoch():
    response = client.get("/api/model/epochs/6.0")
    assert response.status_code == 200
    ep = response.json()
    assert ep["epoch"] == 6.0
    assert ep["step"] == 3000
    assert ep["is_best"] is True
    assert ep["eval_loss"] == 0.0185


def test_get_invalid_epoch():
    response = client.get("/api/model/epochs/99.0")
    assert response.status_code == 404


def test_get_evaluation_metrics():
    response = client.get("/api/model/evaluation")
    assert response.status_code == 200
    data = response.json()
    
    assert "test_metrics" in data
    metrics = data["test_metrics"]
    assert metrics["accuracy"] >= 99.0
    assert metrics["f1_score"] >= 99.0
    assert metrics["total_samples"] == 1000
    
    assert "confusion_matrix" in data
    cm = data["confusion_matrix"]
    assert cm["true_negatives"] + cm["false_positives"] == 500
    assert cm["false_negatives"] + cm["true_positives"] == 500
    assert cm["false_positive_rate"] <= 0.5


def test_get_checkpoints_catalog():
    response = client.get("/api/model/checkpoints")
    assert response.status_code == 200
    checkpoints = response.json()
    assert len(checkpoints) >= 3
    
    ids = [c["checkpoint_id"] for c in checkpoints]
    assert "checkpoint-1000" in ids
    assert "checkpoint-3000" in ids
    assert "checkpoint-5000" in ids


def test_data_cleaner_unit():
    raw = "<p>As an AI language model, here is the text:<div>Deep\u200b learning\u200c systems\ufeff are powerful &amp; fast.</div></p>"
    result = data_cleaner.clean(raw)
    
    assert "<p>" not in result["cleaned_text"]
    assert "<div>" not in result["cleaned_text"]
    assert "\u200b" not in result["cleaned_text"]
    assert "\ufeff" not in result["cleaned_text"]
    assert "As an AI language model" not in result["cleaned_text"]
    assert "Deep learning systems are powerful & fast." in result["cleaned_text"]
    assert result["noise_detected"]["html_tags_count"] >= 2
    assert result["noise_detected"]["zero_width_chars_count"] >= 3
    assert result["noise_detected"]["boilerplate_removed"] is True
    assert result["cleanliness_score"] > 80.0


def test_data_cleaning_api_endpoints():
    # Stats endpoint
    stats_res = client.get("/api/model/data-cleaning/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_raw_samples"] == 10000
    assert stats["total_clean_samples"] == 9620
    assert "noise_breakdown" in stats

    # Samples endpoint
    samples_res = client.get("/api/model/data-cleaning/samples")
    assert samples_res.status_code == 200
    samples = samples_res.json()
    assert len(samples) >= 4

    # Live clean endpoint
    clean_res = client.post("/api/model/data-cleaning/clean", json={
        "text": "<p>Sure! Here is an essay: Test\u200b content.</p>"
    })
    assert clean_res.status_code == 200
    data = clean_res.json()
    assert data["cleaned_text"] == "Test content."
    assert data["noise_detected"]["boilerplate_removed"] is True
