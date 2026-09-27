import os
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.schemas import CommonAuthenticityResult
from backend.app.services.text_service import text_service

class UnifiedContentRouter:
    @staticmethod
    def route_and_analyze(
        text: Optional[str] = None,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Automatically identify content format and dispatch to appropriate system pipeline."""
        if file_bytes and filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".wav", ".mp3", ".m4a", ".ogg"]:
                # Route to Voice Detector
                from backend.app.api.audio import analyze_audio
                # Return routing metadata
                return {
                    "routed_system": "System 4: AI Voice Detector",
                    "file_name": filename,
                    "media_type": "audio",
                    "status": "ready"
                }
            elif ext in [".pdf", ".docx"]:
                # Route to Document Authenticity Detector
                return {
                    "routed_system": "System 3: Document Authenticity Detector",
                    "file_name": filename,
                    "media_type": "document",
                    "status": "ready"
                }
            elif ext in [".txt", ".md"]:
                extracted = file_bytes.decode("utf-8", errors="ignore")
                res = text_service.analyze_text(text=extracted, user_id=user_id, db=db)
                return {
                    "routed_system": "System 1: AI Text Detector",
                    "file_name": filename,
                    "media_type": "text",
                    "result": res
                }

        # Plain text
        if text:
            res = text_service.analyze_text(text=text, user_id=user_id, db=db)
            return {
                "routed_system": "System 1: AI Text Detector",
                "media_type": "text",
                "result": res
            }

        return {
            "routed_system": "Unknown",
            "status": "error",
            "detail": "No valid text or supported file provided."
        }

router_service = UnifiedContentRouter()
