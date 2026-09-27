from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.schemas import (
    PlagiarismAnalyzeRequest,
    PlagiarismAnalyzeResponse
)
from backend.app.services.plagiarism_service import plagiarism_service
from backend.app.core.security import get_current_user_payload

router = APIRouter(prefix="/plagiarism", tags=["System 2: Plagiarism & Paraphrase"])

@router.get("/corpus", response_model=List[Dict[str, Any]])
def list_indexed_corpus(user_payload: dict = Depends(get_current_user_payload)):
    """Returns catalog of all benchmark reference documents indexed in the semantic engine."""
    return plagiarism_service.get_corpus()

@router.post("/analyze", response_model=PlagiarismAnalyzeResponse)
def analyze_plagiarism(
    payload: PlagiarismAnalyzeRequest,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload)
):
    """Scan text against indexed reference corpus for exact copying, semantic paraphrase, and cross-document concordance."""
    user_id = user_payload.get("sub") if isinstance(user_payload, dict) else None
    return plagiarism_service.analyze_plagiarism(payload, user_id=user_id, db=db)
