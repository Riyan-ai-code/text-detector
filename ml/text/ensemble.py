import math
import numpy as np
from typing import Dict, Any, List, Optional

class MetaLearnerEnsemble:
    """
    Phase 2 Meta-Learner Stacking Classifier for TruthLens AI.
    Combines BERT Transformer, Linear TF-IDF, Character-Level Hybrid Ensemble,
    and 26-Dimensional Forensic Stylometrics into a calibrated authenticity score.
    """
    def __init__(self):
        # Base model weights tuned on cross-validation
        self.default_weights = {
            "model_1_bert": 0.50,
            "model_2_linear": 0.20,
            "model_3_char_hybrid": 0.20,
            "forensics_stylometrics": 0.10
        }

    def compute_stacked_prediction(
        self,
        text: str,
        m1_prob: Optional[float] = None,
        m2_prob: Optional[float] = None,
        m3_prob: Optional[float] = None,
        forensic_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically weights model outputs based on document length and forensic signals.
        """
        text = text or ""
        words = text.split()
        word_count = len(words)

        # Ensure valid probability bounds
        m1_prob = float(np.clip(m1_prob, 0.0, 1.0)) if m1_prob is not None else 0.50
        m2_prob = float(np.clip(m2_prob, 0.0, 1.0)) if m2_prob is not None else 0.50
        m3_prob = float(np.clip(m3_prob, 0.0, 1.0)) if m3_prob is not None else 0.50

        # Dynamic weight reallocation based on input length
        weights = dict(self.default_weights)
        if word_count < 35:
            # For short text snippets, character n-grams and linear patterns are more reliable
            weights["model_1_bert"] = 0.30
            weights["model_2_linear"] = 0.30
            weights["model_3_char_hybrid"] = 0.35
            weights["forensics_stylometrics"] = 0.05
        elif word_count > 250:
            # For long essays, deep transformer contextual attention and stylometrics dominate
            weights["model_1_bert"] = 0.55
            weights["model_2_linear"] = 0.15
            weights["model_3_char_hybrid"] = 0.15
            weights["forensics_stylometrics"] = 0.15

        # Normalize weights
        total_w = sum(weights.values())
        norm_weights = {k: v / total_w for k, v in weights.items()}

        # Extract forensic bias score (0.0 to 1.0)
        forensic_ai_score = 0.5
        signals: List[str] = []
        shap_contributions: Dict[str, float] = {}

        if forensic_features:
            metrics = forensic_features.get("metrics", {})
            burstiness = metrics.get("burstiness", 50.0)
            perplexity = metrics.get("perplexity", 50.0)
            lexical = metrics.get("lexical", 50.0)

            # Forensic heuristics
            f_score = 0.5
            if burstiness < 30:
                f_score += 0.20
                signals.append("Uniform sentence cadence (< 30 burstiness)")
            elif burstiness > 70:
                f_score -= 0.20
                signals.append("Natural bursty sentence variations (> 70)")

            if perplexity < 40:
                f_score += 0.15
                signals.append("Highly predictable token sequences")
            elif perplexity > 65:
                f_score -= 0.15
                signals.append("High vocabulary unpredictability and entropy")

            dash_data = forensic_features.get("punctuation_and_dashes", {}).get("dash_metrics", {})
            if dash_data.get("em_dash_per_1k", 0) > 3.0:
                f_score += 0.10
                signals.append("Elevated em-dash density characteristic of LLM structuring")

            forensic_ai_score = max(0.02, min(0.98, f_score))

        # Calculate weighted meta-probability
        blended_prob = (
            (m1_prob * norm_weights["model_1_bert"]) +
            (m2_prob * norm_weights["model_2_linear"]) +
            (m3_prob * norm_weights["model_3_char_hybrid"]) +
            (forensic_ai_score * norm_weights["forensics_stylometrics"])
        )

        # Calibrated Sigmoid scaling around decision boundary
        diff = blended_prob - 0.50
        calibrated_prob = 1.0 / (1.0 + math.exp(-6.0 * diff))

        # Classification mapping
        if calibrated_prob >= 0.82:
            classification = "AI_GENERATED"
            confidence = "HIGH"
        elif calibrated_prob >= 0.60:
            classification = "AI_ASSISTED"
            confidence = "MEDIUM"
        elif calibrated_prob <= 0.20:
            classification = "AUTHENTIC"
            confidence = "HIGH"
        elif calibrated_prob <= 0.40:
            classification = "AUTHENTIC"
            confidence = "MEDIUM"
        else:
            classification = "UNCERTAIN"
            confidence = "LOW"

        # Estimated SHAP-style component contributions
        shap_contributions["BERT_Transformer"] = round((m1_prob - 0.5) * norm_weights["model_1_bert"] * 2.0, 3)
        shap_contributions["Linear_TFIDF"] = round((m2_prob - 0.5) * norm_weights["model_2_linear"] * 2.0, 3)
        shap_contributions["Subword_Char_Hybrid"] = round((m3_prob - 0.5) * norm_weights["model_3_char_hybrid"] * 2.0, 3)
        shap_contributions["Stylometric_Forensics"] = round((forensic_ai_score - 0.5) * norm_weights["forensics_stylometrics"] * 2.0, 3)

        return {
            "classification": classification,
            "probability": round(calibrated_prob, 4),
            "raw_blended_probability": round(blended_prob, 4),
            "confidence": confidence,
            "weights_used": norm_weights,
            "signals": signals,
            "shap_contributions": shap_contributions,
            "forensic_ai_score": round(forensic_ai_score, 3)
        }

meta_learner = MetaLearnerEnsemble()
