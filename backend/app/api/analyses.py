from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import Analysis
from backend.app.models.schemas import AnalysisListItem
from backend.app.core.security import get_current_user_payload

router = APIRouter(prefix="/analyses", tags=["Analysis History"])

@router.get("", response_model=List[AnalysisListItem])
def list_analyses(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload)
):
    """List recent authenticity analyses stored in the platform."""
    query = db.query(Analysis).order_by(Analysis.created_at.desc())
    if user_payload and user_payload.get("sub"):
        # Filter to current user if logged in
        query = query.filter(Analysis.user_id == user_payload["sub"])
        
    records = query.offset(offset).limit(limit).all()
    
    return [
        AnalysisListItem(
            id=r.id,
            content_type=r.content_type,
            file_name=r.file_name,
            classification=r.classification,
            probability=r.probability,
            confidence=r.confidence,
            created_at=str(r.created_at)
        )
        for r in records
    ]

@router.get("/{analysis_id}")
def get_analysis_detail(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve full forensic breakdown for a specific analysis record."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
        
    return {
        "id": analysis.id,
        "content_type": analysis.content_type,
        "file_name": analysis.file_name,
        "classification": analysis.classification,
        "probability": analysis.probability,
        "confidence": analysis.confidence,
        "signals": analysis.signals or [],
        "warnings": analysis.warnings or [],
        "created_at": str(analysis.created_at),
        "text_analysis": {
            "perplexity": analysis.text_analysis.perplexity,
            "burstiness": analysis.text_analysis.burstiness,
            "vocabulary_diversity": analysis.text_analysis.vocabulary_diversity,
            "style_score": analysis.text_analysis.style_score
        } if analysis.text_analysis else None,
        "sentences": [
            {
                "index": s.sentence_index,
                "text": s.text,
                "probability": s.probability,
                "classification": s.classification,
                "signals": s.signals
            }
            for s in analysis.sentences
        ] if analysis.sentences else []
    }

@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Delete an analysis record."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
        
    db.delete(analysis)
    db.commit()
    return {"status": "deleted", "id": analysis_id}
