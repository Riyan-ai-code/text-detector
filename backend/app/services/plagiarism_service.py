import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from ml.plagiarism.semantic_engine import semantic_engine
from backend.app.models.schemas import (
    PlagiarismAnalyzeRequest,
    PlagiarismAnalyzeResponse,
    PlagiarismMatch
)
from backend.app.database.models import Analysis, SimilarityMatch

class PlagiarismService:
    @staticmethod
    def analyze_plagiarism(
        payload: PlagiarismAnalyzeRequest,
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> PlagiarismAnalyzeResponse:
        analysis_id = str(uuid.uuid4())
        text = payload.text.strip()

        # Run hybrid semantic scan
        scan_result = semantic_engine.scan_text(
            text=text,
            threshold=payload.threshold,
            top_k=payload.top_k
        )

        match_items: List[PlagiarismMatch] = [
            PlagiarismMatch(
                source_id=m["source_id"],
                source_title=m["source_title"],
                similarity_score=m["similarity_score"],
                match_type=m["match_type"],
                matched_text=m["matched_text"],
                user_passage=m["user_passage"]
            )
            for m in scan_result["matches"]
        ]

        # Database persistence if DB session provided
        if db is not None:
            try:
                db_analysis = Analysis(
                    id=analysis_id,
                    user_id=user_id,
                    content_type="plagiarism",
                    classification=scan_result["classification"],
                    probability=scan_result["probability"],
                    confidence=scan_result["confidence"],
                    signals=scan_result["signals"],
                    model_version="v3.0.0"
                )
                db.add(db_analysis)

                for m in match_items:
                    db_match = SimilarityMatch(
                        analysis_id=analysis_id,
                        source_id=m.source_id,
                        source_title=m.source_title,
                        similarity_score=m.similarity_score,
                        match_type=m.match_type,
                        matched_text=m.matched_text,
                        user_passage=m.user_passage
                    )
                    db.add(db_match)

                db.commit()
            except Exception as e:
                db.rollback()

        return PlagiarismAnalyzeResponse(
            classification=scan_result["classification"],
            probability=scan_result["probability"],
            confidence=scan_result["confidence"],
            signals=scan_result["signals"],
            analysis_id=analysis_id,
            model_version="v3.0.0",
            overall_similarity=scan_result["overall_similarity"],
            paraphrase_likelihood=scan_result["paraphrase_likelihood"],
            matches=match_items
        )

    @staticmethod
    def get_corpus() -> List[Dict[str, Any]]:
        return semantic_engine.get_indexed_corpus_summary()

plagiarism_service = PlagiarismService()
