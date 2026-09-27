import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.model_service import model_service
from backend.forensic_features import ForensicFeatureExtractor
from ml.text.ensemble import meta_learner
from backend.app.models.schemas import (
    TextAnalyzeResponse,
    SentenceAnalysisItem
)
from backend.app.database.models import Analysis, TextAnalysis, SentenceResult

class TextDetectionService:
    @staticmethod
    def analyze_text(
        text: str,
        model_selection: str = "all",
        return_sentences: bool = True,
        return_shap: bool = True,
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> TextAnalyzeResponse:
        analysis_id = str(uuid.uuid4())
        
        # 1. Run core model inference
        raw_result = model_service.analyze_full(text, selected_model=model_selection)
        forensic_data = raw_result.get("forensic_features", {})
        
        # Extract base stylometrics
        burstiness = float(raw_result.get("burstiness", 50.0))
        perplexity = float(raw_result.get("perplexity", 50.0))
        lexical = float(raw_result.get("lexical", 50.0))
        
        # 2. Phase 2 Meta-Learner Stacking Classifier
        signals: List[str] = []
        shap_contributions: Dict[str, float] = {}

        if model_selection in ("all", "ensemble", "stacking"):
            m1_conf = raw_result.get("model_breakdown", {}).get("model_1", {}).get("confidence")
            m2_conf = raw_result.get("model_breakdown", {}).get("model_2", {}).get("confidence")
            m3_conf = raw_result.get("model_breakdown", {}).get("model_3", {}).get("confidence")
            
            stacked_res = meta_learner.compute_stacked_prediction(
                text=text,
                m1_prob=m1_conf,
                m2_prob=m2_conf,
                m3_prob=m3_conf,
                forensic_features=forensic_data
            )
            
            raw_confidence = stacked_res["probability"]
            classification = stacked_res["classification"]
            confidence_level = stacked_res["confidence"]
            signals.extend(stacked_res.get("signals", []))
            
            if "model_breakdown" in raw_result and raw_result["model_breakdown"]:
                raw_result["model_breakdown"]["meta_learner_stacking"] = {
                    "id": "meta_learner",
                    "name": "Phase 2 Meta-Learner Ensemble",
                    "probability": stacked_res["probability"],
                    "classification": stacked_res["classification"],
                    "confidence": stacked_res["confidence"],
                    "weights_used": stacked_res["weights_used"]
                }
                
            if return_shap:
                shap_contributions = {
                    **stacked_res.get("shap_contributions", {}),
                    "Sentence Uniformity": round((50.0 - burstiness) * 0.30, 1),
                    "Linguistic Predictability": round((50.0 - perplexity) * 0.35, 1),
                    "Vocabulary Repetition": round((50.0 - lexical) * 0.20, 1)
                }
        else:
            # Single model targeted inference
            raw_confidence = float(raw_result.get("confidence", 0.5))
            raw_pred = raw_result.get("prediction", "Uncertain")
            
            if "AI" in raw_pred:
                if raw_confidence > 0.85:
                    classification = "AI_GENERATED"
                    confidence_level = "HIGH"
                elif raw_confidence > 0.65:
                    classification = "AI_ASSISTED"
                    confidence_level = "MEDIUM"
                else:
                    classification = "UNCERTAIN"
                    confidence_level = "LOW"
            else:
                if raw_confidence < 0.25:
                    classification = "AUTHENTIC"
                    confidence_level = "HIGH"
                elif raw_confidence < 0.45:
                    classification = "AUTHENTIC"
                    confidence_level = "MEDIUM"
                else:
                    classification = "UNCERTAIN"
                    confidence_level = "LOW"
                    
            if return_shap:
                shap_contributions = {
                    "Linguistic Predictability": round((50.0 - perplexity) * 0.35, 1),
                    "Sentence Length Uniformity": round((50.0 - burstiness) * 0.30, 1),
                    "Vocabulary Repetition": round((50.0 - lexical) * 0.20, 1),
                    "Syntactic Structure Rhythm": round((raw_confidence - 0.5) * 15.0, 1)
                }
        
        if burstiness < 30.0:
            signals.append("Low sentence-length variation (uniform cadence)")
        elif burstiness > 70.0:
            signals.append("High burstiness variation characteristic of human prose")
            
        if perplexity < 40.0:
            signals.append("High linguistic predictability (standard LLM token sequence)")
        elif perplexity > 65.0:
            signals.append("Elevated lexical surprise and uncommon word choices")
            
        if lexical < 40.0:
            signals.append("Constrained vocabulary diversity")
            
        forensic_data = raw_result.get("forensic_features", {})
        punct_metrics = forensic_data.get("punctuation_and_dashes", {})
        dash_metrics = punct_metrics.get("dash_metrics", {})
        if dash_metrics.get("em_dash_per_1k", 0) > 3.0:
            signals.append("Elevated em-dash density matching synthetic writing patterns")
            
        if not signals:
            signals.append("Linguistic patterns balanced between human and synthetic distributions")
            
        # 4. Sentence-level analysis
        sentence_items: List[SentenceAnalysisItem] = []
        if return_sentences:
            pred_data = model_service.predict(text)
            raw_sentences = pred_data.get("sentence_analysis") or pred_data.get("sentences", [])
            for idx, s in enumerate(raw_sentences):
                s_text = s.get("sentence", s.get("text", "")).strip()
                s_prob = float(s.get("ai_probability", 50.0)) / 100.0 if s.get("ai_probability", 0) > 1.0 else float(s.get("ai_probability", 0.5))
                s_class = "AI-like" if s_prob >= 0.5 else "Human-like"
                s_conf = "HIGH" if s_prob > 0.8 or s_prob < 0.2 else "MEDIUM"

                s_signals = list(s.get("signals", []))
                if len(s_text.split()) < 4 and "Short fragment" not in s_signals:
                    s_signals.append("Short fragment")
                if s_prob > 0.75 and "High syntactic predictability" not in s_signals:
                    s_signals.append("High syntactic predictability")

                sentence_items.append(SentenceAnalysisItem(
                    sentence_index=idx + 1,
                    text=s_text,
                    probability=round(s_prob, 4),
                    classification=s_class,
                    confidence=s_conf,
                    signals=s_signals
                ))

        # 5. SHAP / Feature contributions
        if return_shap and not shap_contributions:
            # Calibrated relative contributions fallback
            pred_factor = (50.0 - perplexity) * 0.35
            burst_factor = (50.0 - burstiness) * 0.30
            lex_factor = (50.0 - lexical) * 0.20
            shap_contributions = {
                "Linguistic Predictability": round(pred_factor, 1),
                "Sentence Length Uniformity": round(burst_factor, 1),
                "Vocabulary Repetition": round(lex_factor, 1),
                "Syntactic Structure Rhythm": round((raw_confidence - 0.5) * 15.0, 1)
            }

        word_count = len(text.split())
        
        # 6. Save to Database if session provided
        if db is not None:
            try:
                db_analysis = Analysis(
                    id=analysis_id,
                    user_id=user_id,
                    content_type="text",
                    classification=classification,
                    probability=round(raw_confidence, 4),
                    confidence=confidence_level,
                    signals=signals,
                    model_version="v2.1.0"
                )
                db.add(db_analysis)
                
                db_text = TextAnalysis(
                    analysis_id=analysis_id,
                    text_length=len(text),
                    perplexity=round(perplexity, 2),
                    burstiness=round(burstiness, 2),
                    vocabulary_diversity=round(lexical, 2),
                    style_score=round(float(raw_result.get("structure", 50.0)), 2),
                    model_version="v2.1.0"
                )
                db.add(db_text)
                
                for s in sentence_items[:50]:  # Cap at 50 per analysis in DB
                    db_sent = SentenceResult(
                        analysis_id=analysis_id,
                        sentence_index=s.sentence_index,
                        text=s.text,
                        probability=s.probability,
                        classification=s.classification,
                        signals=s.signals
                    )
                    db.add(db_sent)
                
                db.commit()
            except Exception as e:
                db.rollback()

        return TextAnalyzeResponse(
            classification=classification,
            probability=round(raw_confidence, 4),
            confidence=confidence_level,
            signals=signals,
            analysis_id=analysis_id,
            model_version="v2.1.0",
            text_length=len(text),
            word_count=word_count,
            counts=raw_result.get("counts"),
            perplexity=round(perplexity, 2),
            burstiness=round(burstiness, 2),
            vocabulary_diversity=round(lexical, 2),
            statistical_signals=raw_result.get("statistical_signals"),
            stylometric_signals=raw_result.get("stylometric_signals"),
            fingerprint_signals=raw_result.get("fingerprint_signals"),
            calibration=raw_result.get("calibration"),
            evasion_audit=raw_result.get("evasion_audit"),
            consensus_matrix=raw_result.get("consensus_matrix"),
            stylometrics=forensic_data,
            sentence_breakdown=sentence_items if return_sentences else None,
            shap_contributions=shap_contributions if return_shap else None,
            model_breakdown=raw_result.get("model_breakdown"),
            authorship_timeline=raw_result.get("authorship_timeline"),
            watermark_analysis=raw_result.get("watermark_analysis"),
            paraphrase_analysis=raw_result.get("paraphrase_analysis"),
            readability=raw_result.get("readability")
        )

text_service = TextDetectionService()
