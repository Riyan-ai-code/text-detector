import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from ml.audio.audio_engine import acoustic_engine
from backend.app.models.schemas import (
    AudioAnalyzeResponse,
    SuspiciousInterval
)
from backend.app.database.models import Analysis, AudioAnalysis

class AudioService:
    @staticmethod
    def analyze_audio_file(
        filename: str,
        contents: bytes,
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> AudioAnalyzeResponse:
        analysis_id = str(uuid.uuid4())

        # 1. Parse signal & sample rate
        signal, sr, duration = acoustic_engine.parse_audio_stream(contents)

        # 2. Extract acoustic metrics
        features = acoustic_engine.extract_features(signal, sr)

        # 3. Detect suspicious temporal intervals
        intervals_raw = acoustic_engine.detect_suspicious_intervals(signal, sr)
        suspicious_intervals = [
            SuspiciousInterval(
                start_time=item["start_time"],
                end_time=item["end_time"],
                score=item["score"],
                reason=item["reason"]
            )
            for item in intervals_raw
        ]

        # 4. Classify synthetic authenticity
        decision = acoustic_engine.classify_audio(features, intervals_raw, duration)

        # 5. Database persistence
        if db is not None:
            try:
                db_analysis = Analysis(
                    id=analysis_id,
                    user_id=user_id,
                    content_type="audio",
                    file_name=filename,
                    classification=decision["classification"],
                    probability=decision["probability"],
                    confidence=decision["confidence"],
                    signals=decision["signals"],
                    model_version="v3.0.0"
                )
                db.add(db_analysis)

                db_audio = AudioAnalysis(
                    analysis_id=analysis_id,
                    duration=duration,
                    sample_rate=sr,
                    synthetic_probability=decision["probability"],
                    model_version="v3.0.0",
                    acoustic_metrics=features,
                    suspicious_intervals=intervals_raw
                )
                db.add(db_audio)
                db.commit()
            except Exception as e:
                db.rollback()

        return AudioAnalyzeResponse(
            classification=decision["classification"],
            probability=decision["probability"],
            confidence=decision["confidence"],
            signals=decision["signals"],
            analysis_id=analysis_id,
            model_version="v3.0.0",
            file_name=filename,
            duration_seconds=duration,
            sample_rate=sr,
            acoustic_features=features,
            suspicious_intervals=suspicious_intervals
        )

audio_service = AudioService()
