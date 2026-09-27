import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.connection import init_db

client = TestClient(app)

def test_init_db():
    """Verify database initialization succeeds without errors."""
    init_db()
    assert True

def test_health_endpoint():
    """Verify system health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["platform"] == "TruthLens AI"
    assert "systems" in data
    assert "system_1_ai_text" in data["systems"]
    assert "system_2_plagiarism" in data["systems"]
    assert "system_3_documents" in data["systems"]
    assert "system_4_voice" in data["systems"]

def test_auth_registration_and_login():
    """Verify user registration, JWT generation, and login."""
    test_email = f"analyst_{os.urandom(4).hex()}@truthlens.ai"
    reg_payload = {
        "email": test_email,
        "name": "Forensic Investigator",
        "password": "SecurePassword2026!"
    }
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == test_email
    
    # 2. Login
    login_payload = {
        "email": test_email,
        "password": "SecurePassword2026!"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

def test_text_analysis_endpoint():
    """Verify text analysis with common authenticity schema."""
    payload = {
        "text": "Artificial intelligence algorithms process large datasets with precision and speed.",
        "model": "all",
        "return_sentences": True,
        "return_shap": True
    }
    res = client.post("/api/text/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "classification" in data
    assert "probability" in data
    assert "confidence" in data
    assert "signals" in data
    assert "warnings" in data
    assert "analysis_id" in data
    assert "sentence_breakdown" in data
    assert "shap_contributions" in data

def test_plagiarism_analysis_endpoint():
    """Verify plagiarism and paraphrase scan endpoint."""
    payload = {
        "text": "The Transformer relies entirely on self-attention mechanisms without sequence-aligned RNNs.",
        "threshold": 0.50
    }
    res = client.post("/api/plagiarism/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "classification" in data
    assert "paraphrase_likelihood" in data
    assert "overall_similarity" in data

if __name__ == "__main__":
    test_init_db()
    test_health_endpoint()
    test_auth_registration_and_login()
    test_text_analysis_endpoint()
    test_plagiarism_analysis_endpoint()
    print("All Phase 1 Foundation tests passed successfully!")
