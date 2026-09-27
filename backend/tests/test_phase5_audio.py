import io
import pytest
import numpy as np
import scipy.io.wavfile as wavfile
from fastapi.testclient import TestClient

from backend.app.main import app
from ml.audio.audio_engine import acoustic_engine
from backend.app.services.audio_service import audio_service

client = TestClient(app)

def create_synthetic_wav_bytes(duration=2.0, sr=16000, freq=440.0) -> bytes:
    """Generates synthetic static sine wave with zero micro-tremor."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Perfectly static tone — vocoder characteristic
    signal = 0.5 * np.sin(2 * np.pi * freq * t)
    int_data = (signal * 32767).astype(np.int16)
    bio = io.BytesIO()
    wavfile.write(bio, sr, int_data)
    return bio.getvalue()

def create_natural_wav_bytes(duration=2.0, sr=16000) -> bytes:
    """Generates expressive dynamic waveform with pitch modulation and varying envelope."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Frequency modulated with natural jitter and amplitude envelope decay/rise
    mod_freq = 150.0 + 35.0 * np.sin(2 * np.pi * 3.0 * t) + 8.0 * np.sin(2 * np.pi * 12.0 * t)
    phase = np.cumsum(2 * np.pi * mod_freq / sr)
    envelope = 0.3 * (1.0 + 0.5 * np.sin(2 * np.pi * 1.5 * t))
    signal = envelope * np.sin(phase)
    # Add subtle harmonic overtones
    signal += 0.15 * envelope * np.sin(2 * phase)
    int_data = (signal * 32767).astype(np.int16)
    bio = io.BytesIO()
    wavfile.write(bio, sr, int_data)
    return bio.getvalue()

def test_synthetic_static_tone_detection():
    """Verify detection of unnaturally rigid synthetic pitch and phase patterns."""
    raw_bytes = create_synthetic_wav_bytes(duration=2.0, freq=440.0)
    signal, sr, dur = acoustic_engine.parse_audio_stream(raw_bytes)
    assert dur >= 1.9
    assert sr == 16000
    features = acoustic_engine.extract_features(signal, sr)
    assert "pitch_stability_f0" in features
    assert "spectral_centroid_hz" in features
    assert "zero_crossing_rate" in features

    decision = acoustic_engine.classify_audio(features, [], dur)
    assert decision["probability"] >= 0.45
    assert any("rigidity" in s or "unnatural" in s or "vocoder" in s for s in decision["signals"])

def test_natural_modulated_waveform():
    """Verify naturalistic pitch and harmonic inflection yields lower synthetic probability."""
    raw_bytes = create_natural_wav_bytes(duration=2.0)
    signal, sr, dur = acoustic_engine.parse_audio_stream(raw_bytes)
    features = acoustic_engine.extract_features(signal, sr)
    assert features["spectral_flatness"] <= 0.40

    decision = acoustic_engine.classify_audio(features, [], dur)
    assert decision["classification"] in ["AUTHENTIC", "POTENTIALLY_MANIPULATED"]
    assert decision["probability"] <= 0.65

def test_suspicious_intervals_detection():
    """Verify windowed temporal interval identification on audio with vocoder artifacts."""
    sr = 16000
    dur = 2.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    # First second: natural; second second: flat buzzing vocoder white noise burst
    sig_nat = 0.4 * np.sin(2 * np.pi * 220 * t[:sr])
    sig_art = 0.4 * np.random.uniform(-1, 1, sr)  # White noise has maximal spectral flatness
    signal = np.concatenate([sig_nat, sig_art]).astype(np.float32)

    intervals = acoustic_engine.detect_suspicious_intervals(signal, sr, window_sec=0.5)
    assert len(intervals) > 0
    top_interval = intervals[0]
    assert "start_time" in top_interval
    assert "end_time" in top_interval
    assert "score" in top_interval
    assert "reason" in top_interval

def test_audio_api_upload_endpoint_e2e():
    """Verify POST /api/audio/analyze end-to-end integration."""
    wav_bytes = create_natural_wav_bytes(duration=1.5)
    files = {"file": ("interview.wav", wav_bytes, "audio/wav")}
    response = client.post("/api/audio/analyze", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "probability" in data
    assert "duration_seconds" in data
    assert data["duration_seconds"] >= 1.4
    assert data["sample_rate"] == 16000
    assert "acoustic_features" in data
    assert "spectral_centroid_hz" in data["acoustic_features"]
    assert "analysis_id" in data

def test_audio_empty_file_rejected():
    """Verify empty 0-byte upload is rejected with 400."""
    files = {"file": ("corrupt.wav", b"", "audio/wav")}
    response = client.post("/api/audio/analyze", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
