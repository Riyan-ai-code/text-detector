from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.schemas import TextAnalyzeRequest, TextAnalyzeResponse
from backend.app.services.text_service import text_service
from backend.app.core.security import get_current_user_payload

router = APIRouter(prefix="/text", tags=["System 1: AI Text Detection"])

@router.post("/analyze", response_model=TextAnalyzeResponse)
def analyze_text_endpoint(
    payload: TextAnalyzeRequest,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload)
):
    """Deep inspect text for AI likelihood, sentence heatmaps, stylometrics, and explainability."""
    text = payload.text.strip()
    if not text or len(text) < 5:
        raise HTTPException(status_code=400, detail="Text must contain at least 5 characters.")
    
    user_id = user_payload.get("sub") if user_payload else None
    
    try:
        return text_service.analyze_text(
            text=text,
            model_selection=payload.model or "all",
            return_sentences=payload.return_sentences,
            return_shap=payload.return_shap,
            user_id=user_id,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis error: {str(e)}")

@router.post("/sentence-analysis")
def sentence_analysis_endpoint(
    payload: TextAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Retrieve sentence-level probability distribution and highlighting metrics."""
    res = text_service.analyze_text(text=payload.text, return_sentences=True, return_shap=False, db=db)
    return {
        "analysis_id": res.analysis_id,
        "sentences": res.sentence_breakdown,
        "overall_probability": res.probability,
        "classification": res.classification
    }

from pydantic import BaseModel, Field
from backend.app.services.comparison_service import ComparisonService
from backend.app.services.watermark_detector import WatermarkDetector
from backend.app.services.paraphrase_detector import ParaphraseDetector
from backend.model_service import model_service

class CompareRequest(BaseModel):
    document_a: str = Field(..., min_length=10)
    document_b: str = Field(..., min_length=10)

class TextPayload(BaseModel):
    text: str = Field(..., min_length=5)

@router.post("/compare")
def compare_documents_endpoint(payload: CompareRequest):
    """Compares Document A vs Document B side-by-side."""
    return ComparisonService.compare(payload.document_a, payload.document_b, model_service)

@router.post("/watermark")
def watermark_analysis_endpoint(payload: TextPayload):
    """Statistical AI watermark verification (Kirchenbauer et al. framework)."""
    return WatermarkDetector.analyze(payload.text)

@router.post("/paraphrase")
def paraphrase_detection_endpoint(payload: TextPayload):
    """Detects automated AI text spinning and unnatural synonym substitutions."""
    return ParaphraseDetector.detect(payload.text)
