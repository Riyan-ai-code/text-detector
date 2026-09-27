import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.schemas import DocumentAnalyzeResponse
from backend.app.services.document_forensics import document_forensics
from backend.app.core.security import get_current_user_payload

router = APIRouter(prefix="/documents", tags=["System 3: Document Authenticity"])

@router.post("/analyze", response_model=DocumentAnalyzeResponse)
async def analyze_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload)
):
    """Inspect PDF, DOCX, or TXT documents for metadata provenance, typography anomalies, invisible characters, citations, and AI text."""
    filename = file.filename or "document.txt"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported document format '{ext}'. Supported formats: .pdf, .docx, .txt"
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded document file is empty (0 bytes)."
        )

    user_id = user_payload.get("sub") if isinstance(user_payload, dict) else None

    try:
        return document_forensics.analyze_document_file(
            filename=filename,
            contents=contents,
            user_id=user_id,
            db=db
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing document '{filename}': {str(e)}"
        )
