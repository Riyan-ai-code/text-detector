import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.schemas import AudioAnalyzeResponse
from backend.app.services.audio_service import audio_service
from backend.app.core.security import get_current_user_payload

router = APIRouter(prefix="/audio", tags=["System 4: AI Voice Detector"])

@router.post("/analyze", response_model=AudioAnalyzeResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload)
):
    """Analyze speech recording (WAV, MP3, M4A, OGG) for synthetic generation, vocoder artifacts, and voice cloning."""
    filename = file.filename or "recording.wav"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".wav", ".mp3", ".m4a", ".ogg"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format '{ext}'. Supported formats: .wav, .mp3, .m4a, .ogg"
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded audio file is empty (0 bytes).")

    user_id = user_payload.get("sub") if isinstance(user_payload, dict) else None

    try:
        return audio_service.analyze_audio_file(
            filename=filename,
            contents=contents,
            user_id=user_id,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing audio: {str(e)}")
