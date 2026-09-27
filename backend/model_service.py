import os
import re
import math
from typing import Dict, Any, List, Optional
from collections import Counter
import numpy as np
import joblib
from scipy.sparse import hstack
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from backend.forensic_features import ForensicFeatureExtractor
from backend.app.services.evasion_service import EvasionService
from backend.app.services.statistical_analyzer import StatisticalAnalyzer
from backend.app.services.stylometric_analyzer import StylometricAnalyzer
from backend.app.services.fingerprint_analyzer import FingerprintAnalyzer
from backend.app.services.calibration_service import CalibrationService
from backend.app.services.authorship_segmenter import AuthorshipSegmenter
from backend.app.services.watermark_detector import WatermarkDetector
from backend.app.services.paraphrase_detector import ParaphraseDetector

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_DIR = os.path.join(BASE_DIR, "model", "bert_ai_detector", "checkpoint-1500")
FALLBACK_BERT_DIR = os.path.join(BASE_DIR, "model", "bert_ai_detector")
ML_MODELS_DIR = os.path.join(BASE_DIR, "model", "ml_models")


class LinguisticAnalyzer:
    """
    Calculates stylometric, readability, and information-theoretic metrics
    for deep linguistic forensics.
    """

    @staticmethod
    def count_syllables(word: str) -> int:
        """Heuristic syllable counter for readability metrics."""
        w = word.lower().strip()
        if len(w) <= 3:
            return 1
        w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
        w = re.sub(r"^y", "", w)
        matches = re.findall(r"[aeiouy]{1,2}", w)
        return max(1, len(matches))

    @classmethod
    def analyze(cls, text: str) -> dict:
        if not text or not text.strip():
            return {
                "lexical": 50.0,
                "structure": 50.0,
                "burstiness": 50.0,
                "coherence": 50.0,
                "perplexity": 50.0,
                "flesch_reading_ease": 60.0,
                "flesch_kincaid_grade": 8.0,
                "grade_level_label": "Standard High School (Grade 8-9)",
                "simpsons_diversity": 0.85,
                "binoculars_contrast": 50.0,
                "genre_tone": "General Prose",
                "reading_time_seconds": 0
            }

        words = re.findall(r"\b[\w'-]+\b", text.lower())
        raw_words = re.findall(r"\b[\w'-]+\b", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        if not words or not sentences:
            return {
                "lexical": 50.0,
                "structure": 50.0,
                "burstiness": 50.0,
                "coherence": 50.0,
                "perplexity": 50.0,
                "flesch_reading_ease": 60.0,
                "flesch_kincaid_grade": 8.0,
                "grade_level_label": "Standard High School (Grade 8-9)",
                "simpsons_diversity": 0.85,
                "binoculars_contrast": 50.0,
                "genre_tone": "General Prose",
                "reading_time_seconds": 0
            }

        total_words = len(words)
        total_sentences = len(sentences)

        # 1. Lexical Richness (Type-Token Ratio & Avg Word Length)
        unique_words = set(words)
        ttr = len(unique_words) / total_words
        avg_word_len = sum(len(w) for w in words) / total_words
        lexical = min(100.0, max(0.0, (ttr * 65.0) + (avg_word_len * 6.0)))

        # 2. Sentence Length Variation & Structural Density
        sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
        avg_sent_len = sum(sentence_lengths) / total_sentences

        if len(sentence_lengths) > 1:
            sent_std = float(np.std(sentence_lengths))
        else:
            sent_std = 0.0

        structure = min(100.0, max(0.0, 40.0 + (sent_std * 3.5) + (avg_sent_len * 1.2)))

        # 3. Burstiness (Variation of sentence lengths over mean length)
        if avg_sent_len > 0 and len(sentence_lengths) > 1:
            burstiness_val = (sent_std / (avg_sent_len + 1e-5)) * 100.0
            burstiness = min(100.0, max(0.0, burstiness_val * 1.5))
        else:
            burstiness = 35.0

        # 4. Coherence (Vocabulary overlap between consecutive sentences)
        overlaps = []
        for i in range(len(sentences) - 1):
            w1 = set(re.findall(r"\b\w+\b", sentences[i].lower()))
            w2 = set(re.findall(r"\b\w+\b", sentences[i + 1].lower()))
            if w1 and w2:
                jaccard = len(w1.intersection(w2)) / len(w1.union(w2))
                overlaps.append(jaccard)

        if overlaps:
            coherence = min(100.0, max(0.0, (sum(overlaps) / len(overlaps)) * 250.0 + 30.0))
        else:
            coherence = 65.0

        # 5. Perplexity (Proxy using character and subword entropy)
        char_counts = Counter(text.lower())
        entropy = 0.0
        for c, count in char_counts.items():
            p = count / len(text)
            entropy -= p * math.log2(p)

        perplexity = min(100.0, max(0.0, (entropy * 14.5) + (100.0 - lexical) * 0.25))

        # 6. Readability: Flesch Reading Ease & Flesch-Kincaid Grade
        total_syllables = sum(cls.count_syllables(w) for w in words)
        words_per_sent = total_words / max(total_sentences, 1)
        syllables_per_word = total_syllables / max(total_words, 1)

        flesch_ease = 206.835 - (1.015 * words_per_sent) - (84.6 * syllables_per_word)
        flesch_ease = round(float(np.clip(flesch_ease, 0.0, 100.0)), 1)

        fk_grade = (0.39 * words_per_sent) + (11.8 * syllables_per_word) - 15.59
        fk_grade = round(float(max(1.0, fk_grade)), 1)

        if fk_grade >= 16.0:
            grade_label = f"Post-Graduate / Scholarly (Grade {fk_grade})"
        elif fk_grade >= 13.0:
            grade_label = f"College Level (Grade {fk_grade})"
        elif fk_grade >= 10.0:
            grade_label = f"High School Advanced (Grade {fk_grade})"
        elif fk_grade >= 7.0:
            grade_label = f"Middle School (Grade {fk_grade})"
        else:
            grade_label = f"Elementary / Plain Text (Grade {fk_grade})"

        # 7. Simpson's Diversity Index: D = 1 - sum(n*(n-1)) / (N*(N-1))
        if total_words > 1:
            word_counts = Counter(words)
            numerator = sum(count * (count - 1) for count in word_counts.values())
            simpson = 1.0 - (numerator / (total_words * (total_words - 1)))
            simpsons_diversity = round(float(np.clip(simpson, 0.0, 1.0)), 3)
        else:
            simpsons_diversity = 1.0

        # 8. Binoculars-style Normalized Contrastive Perplexity Metric
        # Evaluates the gap between formulaic n-gram predictability and context dispersion
        # LLM text exhibits unusually low perplexity gap compared to human idiosyncratic writing
        contrast_ratio = (perplexity / max(10.0, 100.0 - burstiness)) * 50.0
        binoculars_contrast = round(float(np.clip(contrast_ratio, 10.0, 95.0)), 1)

        # 9. Genre / Tone Heuristic Classification
        first_person_count = sum(1 for w in words if w in {"i", "me", "my", "we", "our", "myself"})
        passive_markers = sum(1 for w in words if w in {"is", "was", "were", "been", "being"})
        academic_jargon = sum(1 for w in words if len(w) >= 9)

        if academic_jargon / total_words > 0.18 and words_per_sent > 18:
            genre_tone = "Academic / Formal Research"
        elif first_person_count / total_words > 0.04 and burstiness > 60:
            genre_tone = "Conversational / Personal Memoir"
        elif "function" in text.lower() or "algorithm" in text.lower() or "data" in text.lower() or "system" in text.lower():
            genre_tone = "Technical / Analytical"
        elif words_per_sent < 14 and ttr > 0.65:
            genre_tone = "Journalistic / News Editorial"
        elif "delve" in words or "revolutionize" in words or "testament" in words or "unprecedented" in words:
            genre_tone = "Synthetic Marketing / Promotional"
        else:
            genre_tone = "General Informational Prose"

        reading_time_seconds = math.ceil((total_words / 200.0) * 60)

        return {
            "lexical": round(float(lexical), 2),
            "structure": round(float(structure), 2),
            "burstiness": round(float(burstiness), 2),
            "coherence": round(float(coherence), 2),
            "perplexity": round(float(perplexity), 2),
            "flesch_reading_ease": flesch_ease,
            "flesch_kincaid_grade": fk_grade,
            "grade_level_label": grade_label,
            "simpsons_diversity": simpsons_diversity,
            "binoculars_contrast": binoculars_contrast,
            "genre_tone": genre_tone,
            "reading_time_seconds": reading_time_seconds
        }


class ModelService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.id2label = {0: "HUMAN", 1: "AI_GENERATED"}
        self.label2id = {"HUMAN": 0, "AI_GENERATED": 1}

        # Model 2 & Model 3 artifacts
        self.m2_vec = None
        self.m2_ensemble = None
        self.m3_word_vec = None
        self.m3_char_vec = None
        self.m3_ensemble = None

        self.load_all_models()

    def load_all_models(self):
        self._load_bert_model()
        self._load_scikit_models()

    def _load_bert_model(self):
        model_path = CHECKPOINT_DIR if os.path.exists(CHECKPOINT_DIR) else FALLBACK_BERT_DIR
        print(f"[ModelService] Loading BERT model from: {model_path} on device: {self.device}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            if hasattr(self.model.config, "id2label") and self.model.config.id2label:
                self.id2label = {int(k): v for k, v in self.model.config.id2label.items()}
            print(f"[ModelService] Successfully loaded fine-tuned BERT model.")
        except Exception as e:
            print(f"[ModelService Warning] Error loading BERT model: {e}")

    def _load_scikit_models(self):
        models_dir = ML_MODELS_DIR
        if not os.path.exists(models_dir):
            print(f"[ModelService Warning] Scikit models directory not found at {models_dir}")
            return

        try:
            m2_vec_path = os.path.join(models_dir, "model2_vectorizer.joblib")
            m2_ens_path = os.path.join(models_dir, "model2_ensemble.joblib")
            if os.path.exists(m2_vec_path) and os.path.exists(m2_ens_path):
                self.m2_vec = joblib.load(m2_vec_path)
                self.m2_ensemble = joblib.load(m2_ens_path)
                print(f"[ModelService] Successfully loaded Model 2 (Logistic Regression + SGD Classifier)")

            m3_wvec_path = os.path.join(models_dir, "model3_word_vec.joblib")
            m3_cvec_path = os.path.join(models_dir, "model3_char_vec.joblib")
            m3_ens_path = os.path.join(models_dir, "model3_ensemble.joblib")
            if os.path.exists(m3_wvec_path) and os.path.exists(m3_cvec_path) and os.path.exists(m3_ens_path):
                self.m3_word_vec = joblib.load(m3_wvec_path)
                self.m3_char_vec = joblib.load(m3_cvec_path)
                self.m3_ensemble = joblib.load(m3_ens_path)
                print(f"[ModelService] Successfully loaded Model 3 (Dual Word/Char TF-IDF Hybrid Ensemble)")
        except Exception as e:
            print(f"[ModelService Warning] Error loading scikit-learn models: {e}")

    def split_sentences(self, text: str) -> List[str]:
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        raw_sentences = sentence_endings.split(text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        return sentences if sentences else [text.strip()]

    def compute_text_statistics(self, text: str) -> Dict[str, Any]:
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        char_count = len(text)
        sentences = self.split_sentences(text)
        sentence_count = max(len(sentences), 1)
        
        avg_sentence_len = round(word_count / sentence_count, 1) if sentence_count > 0 else 0
        
        sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        if len(sentence_lengths) > 1:
            mean_len = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            burstiness = round(math.sqrt(variance), 2)
        else:
            burstiness = 0.0

        unique_words = set(w.lower() for w in words)
        lexical_diversity = round((len(unique_words) / word_count) * 100, 1) if word_count > 0 else 0
        reading_time_sec = math.ceil((word_count / 200) * 60)

        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_len,
            "burstiness_score": burstiness,
            "lexical_diversity_pct": lexical_diversity,
            "reading_time_seconds": reading_time_sec
        }

    def predict_sentence_batch(self, sentences: List[str]) -> List[Dict[str, Any]]:
        if not sentences:
            return []

        results = []
        raw_probs = []

        # 1. Primary Transformer Batch Inference if Available
        if self.model is not None and self.tokenizer is not None:
            try:
                with torch.no_grad():
                    inputs = self.tokenizer(
                        sentences,
                        padding=True,
                        truncation=True,
                        max_length=256,
                        return_tensors="pt"
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    outputs = self.model(**inputs)
                    probs_matrix = F.softmax(outputs.logits, dim=-1).cpu().numpy()
                    for idx in range(len(sentences)):
                        raw_probs.append((float(probs_matrix[idx][0]), float(probs_matrix[idx][1])))
            except Exception as e:
                print(f"[ModelService] Batch sentence transformer inference failed: {e}")
                raw_probs = []

        # Calculate mean sentence length across input for burstiness comparison
        all_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
        mean_len = float(np.mean(all_lengths)) if all_lengths else 12.0

        for idx, sentence in enumerate(sentences):
            words = re.findall(r"\b[\w'-]+\b", sentence.lower())
            w_count = max(1, len(words))

            # Resolve AI probability
            if raw_probs and idx < len(raw_probs):
                human_score = raw_probs[idx][0]
                ai_score = raw_probs[idx][1]
            else:
                # Stylometric proxy for sentence
                sent_metrics = LinguisticAnalyzer.analyze(sentence)
                ai_score = (
                    (1.0 - (sent_metrics["burstiness"] / 100.0)) * 0.35 +
                    (sent_metrics["coherence"] / 100.0) * 0.25 +
                    (1.0 - (sent_metrics["perplexity"] / 100.0)) * 0.20 +
                    (1.0 - (sent_metrics["lexical"] / 100.0)) * 0.20
                )
                ai_score = float(np.clip(ai_score, 0.05, 0.95))
                human_score = 1.0 - ai_score

            # Detect cliches in this specific sentence
            evasion_res = EvasionService.scan_and_sanitize(sentence)
            sentence_cliches = [c["phrase"] for c in evasion_res.get("ai_cliches_found", [])]

            # Adjust AI score if heavy cliches detected
            if sentence_cliches:
                ai_score = min(0.98, ai_score + 0.12 * len(sentence_cliches))
                human_score = 1.0 - ai_score

            is_ai = ai_score >= 0.50
            label = "AI_GENERATED" if is_ai else "HUMAN"
            confidence = ai_score if is_ai else human_score

            # Granular highlight level & status
            if ai_score >= 0.75:
                highlight_level = "high_ai"
                status_label = "High AI (Flagged)"
                conf_label = "High" if ai_score >= 0.85 else "Medium"
            elif ai_score >= 0.50:
                highlight_level = "med_ai"
                status_label = "Moderate AI"
                conf_label = "Medium"
            elif ai_score >= 0.35:
                highlight_level = "low_ai"
                status_label = "Mixed / Uncertain"
                conf_label = "Low"
            else:
                highlight_level = "human"
                status_label = "Likely Human"
                conf_label = "High" if human_score >= 0.80 else "Medium"

            # Granular signals conforming to explainability spec
            signals = []
            if ai_score >= 0.60:
                signals.append("High predictability")
                if abs(w_count - mean_len) < 3.0:
                    signals.append("Low sentence-length variation")
                if sentence_cliches or w_count >= 16:
                    signals.append("Repeated syntactic structure")
                if len(set(words)) / max(w_count, 1) < 0.85:
                    signals.append("Low vocabulary variation")
                if sentence_cliches:
                    signals.append(f"AI Cliché: '{sentence_cliches[0]}'")
            else:
                signals.append("Natural predictability & surprise")
                if abs(w_count - mean_len) >= 3.0:
                    signals.append("Variable sentence length")
                signals.append("Organic syntactic structure")
                signals.append("Rich vocabulary variation")

            # Readability for sentence
            sent_syllables = sum(LinguisticAnalyzer.count_syllables(w) for w in words)
            ease = 206.835 - (1.015 * w_count) - (84.6 * (sent_syllables / w_count))
            ease = round(float(np.clip(ease, 0.0, 100.0)), 1)

            results.append({
                "sentence_index": idx + 1,
                "sentence": sentence,
                "label": label,
                "ai_probability": round(ai_score * 100, 2),
                "ai_like_score": round(ai_score * 100, 1),
                "human_probability": round(human_score * 100, 2),
                "confidence": round(confidence * 100, 2),
                "confidence_label": conf_label,
                "highlight_level": highlight_level,
                "status_label": status_label,
                "word_count": w_count,
                "reading_ease": ease,
                "cliches": sentence_cliches,
                "signals": signals if signals else ["Standard linguistic profile"]
            })

        return results

    def _compute_forensic_score(self, text: str) -> float:
        """Extracts calibrated forensic likelihood from burstiness, perplexity, and LLM clichés."""
        metrics = LinguisticAnalyzer.analyze(text)
        b_norm = metrics['burstiness'] / 100.0
        p_norm = metrics['perplexity'] / 100.0
        
        lower_t = text.lower()
        cliches = [
            "delve into", "delves into", "testament to", "rich tapestry", "tapestry",
            "multifaceted", "rapidly evolving", "crucial role", "in conclusion",
            "furthermore", "moreover", "harness the power", "pivotal role", "beacon of",
            "plays a vital role", "stands as a testament", "in today's digital landscape"
        ]
        cliche_count = sum(1 for c in cliches if c in lower_t)
        
        score = 0.50
        if b_norm < 0.35:
            score += 0.20
        elif b_norm > 0.65:
            score -= 0.25
        elif b_norm > 0.50:
            score -= 0.15
            
        if p_norm < 0.35:
            score += 0.15
        elif p_norm > 0.65:
            score -= 0.15
            
        if cliche_count > 0:
            score += min(0.30, cliche_count * 0.12)
            
        return float(np.clip(score, 0.02, 0.98))

    def predict_model_1(self, text: str) -> dict:
        """Model 1: Fine-tuned BERT Transformer Neural Classifier."""
        if not text or not text.strip():
            return {"prediction": "Likely Human", "confidence": 0.50}

        forensic_prior = self._compute_forensic_score(text)
        raw_bert_ai = None

        if self.model is not None and self.tokenizer is not None:
            try:
                with torch.no_grad():
                    inputs = self.tokenizer(
                        text,
                        padding=True,
                        truncation=True,
                        max_length=512,
                        return_tensors="pt"
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    outputs = self.model(**inputs)
                    probs = F.softmax(outputs.logits, dim=-1).cpu().squeeze().tolist()

                if isinstance(probs, float):
                    probs = [1.0 - probs, probs]
                raw_bert_ai = float(probs[1])
            except Exception as e:
                print(f"[ModelService] BERT inference fallback on text: {e}")

        if raw_bert_ai is not None:
            # Calibrate BERT output with stylometrics:
            # If text has heavy cliches or very low burstiness, bias toward AI
            # If text is bursty human narrative without cliches, bias toward Human
            blended = (0.65 * raw_bert_ai) + (0.35 * forensic_prior)
            conf = float(np.clip(blended, 0.01, 0.99))
        else:
            conf = forensic_prior

        return {
            "prediction": "Likely AI" if conf >= 0.5 else "Likely Human",
            "confidence": round(conf, 4)
        }

    def predict_model_2(self, text: str) -> dict:
        """Model 2: Logistic Regression + SGD Classifier."""
        if not self.m2_vec or not self.m2_ensemble:
            return self.predict_model_1(text)

        try:
            X = self.m2_vec.transform([text])
            prob_ai = float(self.m2_ensemble.predict_proba(X)[0, 1])
            forensic_prior = self._compute_forensic_score(text)
            calibrated = (0.60 * prob_ai) + (0.40 * forensic_prior)
            conf = float(np.clip(calibrated, 0.01, 0.99))
            return {
                "prediction": "Likely AI" if conf >= 0.5 else "Likely Human",
                "confidence": round(conf, 4)
            }
        except Exception as e:
            print(f"[ModelService] Model 2 prediction error: {e}")
            return self.predict_model_1(text)

    def predict_model_3(self, text: str) -> dict:
        """Model 3: Hybrid Stacking Ensemble (MultinomialNB + SGD + Dual TF-IDF)."""
        if not self.m3_word_vec or not self.m3_char_vec or not self.m3_ensemble:
            return self.predict_model_2(text)

        try:
            X_word = self.m3_word_vec.transform([text])
            X_char = self.m3_char_vec.transform([text])
            X = hstack([X_word, X_char]).tocsr()
            prob_ai = float(self.m3_ensemble.predict_proba(X)[0, 1])
            forensic_prior = self._compute_forensic_score(text)
            calibrated = (0.65 * prob_ai) + (0.35 * forensic_prior)
            conf = float(np.clip(calibrated, 0.01, 0.99))
            return {
                "prediction": "Likely AI" if conf >= 0.5 else "Likely Human",
                "confidence": round(conf, 4)
            }
        except Exception as e:
            print(f"[ModelService] Model 3 prediction error: {e}")
            return self.predict_model_2(text)

    def analyze_full(self, text: str, selected_model: str = "all") -> dict:
        """Runs the requested model(s) and returns formatted breakdown for the React Dashboard."""
        # 1. Evasion Audit & Text Sanitization
        evasion_audit = EvasionService.scan_and_sanitize(text)
        clean_text = evasion_audit["sanitized_text"] if evasion_audit["is_tampered"] else text

        metrics = LinguisticAnalyzer.analyze(clean_text)
        empty_model_res = {"prediction": "N/A", "confidence": None}

        # 2. Evaluate Models
        m1_res = self.predict_model_1(clean_text)
        m2_res = self.predict_model_2(clean_text)
        m3_res = self.predict_model_3(clean_text)

        # 3. Model Consensus Matrix Calculation
        m1_p = m1_res.get("prediction", "")
        m2_p = m2_res.get("prediction", "")
        m3_p = m3_res.get("prediction", "")

        ai_votes = sum(1 for p in [m1_p, m2_p, m3_p] if "AI" in p)
        human_votes = 3 - ai_votes

        if ai_votes == 3:
            consensus_status = "UNANIMOUS_AI"
            consensus_verdict = "Unanimous AI Detection"
            consensus_badge = "100% Unanimous Agreement"
            consensus_color = "#f87171"
        elif human_votes == 3:
            consensus_status = "UNANIMOUS_HUMAN"
            consensus_verdict = "Unanimous Human Authenticity"
            consensus_badge = "100% Unanimous Agreement"
            consensus_color = "#4ade80"
        elif ai_votes == 2:
            consensus_status = "MAJORITY_AI"
            consensus_verdict = "Consensus AI (2 of 3 Models)"
            consensus_badge = "66.7% Majority Agreement"
            consensus_color = "#fb923c"
        else:
            consensus_status = "MAJORITY_HUMAN"
            consensus_verdict = "Consensus Human (2 of 3 Models)"
            consensus_badge = "66.7% Majority Agreement"
            consensus_color = "#a3e635"

        consensus_matrix = {
            "status": consensus_status,
            "verdict": consensus_verdict,
            "badge": consensus_badge,
            "color": consensus_color,
            "ai_votes": ai_votes,
            "human_votes": human_votes,
            "total_models": 3,
            "agreement_pct": round((max(ai_votes, human_votes) / 3.0) * 100, 1),
            "model_votes": [
                {
                    "id": "model_1",
                    "name": "BERT Transformer",
                    "vote": "AI" if "AI" in m1_p else "HUMAN",
                    "confidence": m1_res.get("confidence"),
                    "weight": 0.50
                },
                {
                    "id": "model_2",
                    "name": "Logistic Regression + SGD",
                    "vote": "AI" if "AI" in m2_p else "HUMAN",
                    "confidence": m2_res.get("confidence"),
                    "weight": 0.25
                },
                {
                    "id": "model_3",
                    "name": "Dual TF-IDF Hybrid",
                    "vote": "AI" if "AI" in m3_p else "HUMAN",
                    "confidence": m3_res.get("confidence"),
                    "weight": 0.25
                }
            ]
        }

        # Determine target verdict & confidence based on selected_model
        if selected_model == "model_1":
            target_verdict = m1_res["prediction"]
            target_conf = m1_res["confidence"]
            combined_res = empty_model_res
        elif selected_model == "model_2":
            target_verdict = m2_res["prediction"]
            target_conf = m2_res["confidence"]
            combined_res = empty_model_res
        elif selected_model == "model_3":
            target_verdict = m3_res["prediction"]
            target_conf = m3_res["confidence"]
            combined_res = empty_model_res
        else:
            from ml.text.ensemble import meta_learner
            stacked_res = meta_learner.compute_stacked_prediction(
                text=clean_text,
                m1_prob=m1_res["confidence"] if "AI" in m1_res["prediction"] else (1.0 - m1_res["confidence"]),
                m2_prob=m2_res["confidence"] if "AI" in m2_res["prediction"] else (1.0 - m2_res["confidence"]),
                m3_prob=m3_res["confidence"] if "AI" in m3_res["prediction"] else (1.0 - m3_res["confidence"]),
                forensic_features={"metrics": {"burstiness": metrics["burstiness"], "perplexity": metrics["perplexity"], "lexical": metrics["lexical"]}}
            )
            combined_conf = round(float(np.clip(stacked_res["probability"], 0.01, 0.99)), 4)
            combined_verdict = "Likely AI" if combined_conf >= 0.5 else "Likely Human"
            combined_res = {"prediction": combined_verdict, "confidence": combined_conf}
            target_verdict = combined_verdict
            target_conf = combined_conf

        forensic_data = ForensicFeatureExtractor.extract_all(clean_text)

        # 4. Phase 1 Multi-Signal Forensics & Calibration
        stat_signals = StatisticalAnalyzer.analyze(clean_text)
        stylo_signals = StylometricAnalyzer.analyze(clean_text)
        fingerprint_signals = FingerprintAnalyzer.analyze(clean_text)

        agreement_ratio = 1.0 if consensus_matrix.get("is_unanimous") else 0.67
        raw_prob_val = target_conf if "AI" in target_verdict else (1.0 - target_conf)
        calibration_data = CalibrationService.calibrate(
            text=clean_text,
            word_count=stat_signals["counts"]["word_count"],
            raw_probability=raw_prob_val,
            model_agreement_ratio=agreement_ratio,
            statistical_signals=stat_signals,
            stylometric_signals=stylo_signals
        )

        # 5. Enriched Sentence-Level Analysis for Heatmap
        sentences = self.split_sentences(text)
        sentence_analysis = self.predict_sentence_batch(sentences)

        # 6. Mixed Authorship Timeline & Transitions
        authorship_timeline = AuthorshipSegmenter.segment(clean_text, self)

        # 7. Experimental Modules: Watermark & Paraphrase/Spin
        watermark_analysis = WatermarkDetector.analyze(clean_text)
        paraphrase_analysis = ParaphraseDetector.detect(clean_text)

        ai_sentences = sum(1 for s in sentence_analysis if s.get("ai_probability", 0) >= 50.0)
        human_sentences = len(sentence_analysis) - ai_sentences

        return {
            "active_model": selected_model,
            "prediction": target_verdict,
            "confidence": target_conf,
            "lexical": metrics["lexical"],
            "structure": metrics["structure"],
            "burstiness": metrics["burstiness"],
            "coherence": metrics["coherence"],
            "perplexity": metrics["perplexity"],
            "counts": stat_signals["counts"],
            "statistical_signals": stat_signals,
            "stylometric_signals": stylo_signals,
            "fingerprint_signals": fingerprint_signals,
            "calibration": calibration_data,
            "authorship_timeline": authorship_timeline,
            "watermark_analysis": watermark_analysis,
            "paraphrase_analysis": paraphrase_analysis,
            "readability": {
                "flesch_reading_ease": metrics["flesch_reading_ease"],
                "flesch_kincaid_grade": metrics["flesch_kincaid_grade"],
                "grade_level_label": metrics["grade_level_label"],
                "reading_time_seconds": metrics["reading_time_seconds"]
            },
            "stylometrics": {
                "simpsons_diversity": metrics["simpsons_diversity"],
                "binoculars_contrast": metrics["binoculars_contrast"],
                "genre_tone": metrics["genre_tone"]
            },
            "evasion_audit": evasion_audit,
            "consensus_matrix": consensus_matrix,
            "forensic_features": forensic_data,
            "sentence_analysis": sentence_analysis,
            "sentences": sentence_analysis,
            "sentence_breakdown": {
                "total_sentences": len(sentence_analysis),
                "ai_sentences": ai_sentences,
                "human_sentences": human_sentences,
                "ai_ratio_pct": round((ai_sentences / max(len(sentence_analysis), 1)) * 100, 1)
            },
            "model_breakdown": {
                "model_1": {
                    "id": "model_1",
                    "name": "Model 1: BERT Transformer",
                    "prediction": m1_res["prediction"],
                    "confidence": m1_res["confidence"]
                },
                "model_2": {
                    "id": "model_2",
                    "name": "Model 2: Logistic Regression + SGD",
                    "prediction": m2_res["prediction"],
                    "confidence": m2_res["confidence"]
                },
                "model_3": {
                    "id": "model_3",
                    "name": "Model 3: Dual TF-IDF Hybrid Ensemble",
                    "prediction": m3_res["prediction"],
                    "confidence": m3_res["confidence"]
                },
                "combined": {
                    "id": "all",
                    "name": "All 3 Models (Weighted Ensemble)",
                    "prediction": combined_res["prediction"],
                    "confidence": combined_res["confidence"]
                }
            }
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """Deep inference with document probabilities, sentence heatmaps, and stats."""
        text = text.strip()
        if not text:
            raise ValueError("Input text cannot be empty.")

        evasion_audit = EvasionService.scan_and_sanitize(text)
        clean_text = evasion_audit["sanitized_text"] if evasion_audit["is_tampered"] else text

        # Document-level prediction via BERT if available
        if self.model is not None and self.tokenizer is not None:
            with torch.no_grad():
                inputs = self.tokenizer(
                    clean_text,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                probs = F.softmax(outputs.logits, dim=-1).cpu().squeeze().tolist()

            if isinstance(probs, float):
                probs = [1.0 - probs, probs]
            human_prob = float(probs[0])
            ai_prob = float(probs[1])
        else:
            m1 = self.predict_model_1(clean_text)
            ai_prob = m1["confidence"] if m1["prediction"] == "Likely AI" else (1.0 - m1["confidence"])
            human_prob = 1.0 - ai_prob

        # Classification label
        if ai_prob >= 0.60:
            verdict = "AI_GENERATED"
            verdict_text = "Likely AI-Generated"
            overall_confidence = ai_prob
        elif human_prob >= 0.60:
            verdict = "HUMAN"
            verdict_text = "Likely Human-Written"
            overall_confidence = human_prob
        else:
            verdict = "MIXED_OR_UNCERTAIN"
            verdict_text = "Mixed or Uncertain"
            overall_confidence = max(ai_prob, human_prob)

        # Sentence-level analysis
        sentences = self.split_sentences(text)
        sentence_analysis = self.predict_sentence_batch(sentences)

        # Linguistic stats
        stats = self.compute_text_statistics(clean_text)
        linguistic = LinguisticAnalyzer.analyze(clean_text)

        ai_sentence_count = sum(1 for s in sentence_analysis if s["ai_probability"] >= 50.0)
        human_sentence_count = len(sentence_analysis) - ai_sentence_count

        return {
            "verdict": verdict,
            "verdict_text": verdict_text,
            "ai_probability": round(ai_prob * 100, 2),
            "human_probability": round(human_prob * 100, 2),
            "confidence": round(overall_confidence * 100, 2),
            "sentence_analysis": sentence_analysis,
            "sentence_breakdown": {
                "total_sentences": len(sentence_analysis),
                "ai_sentences": ai_sentence_count,
                "human_sentences": human_sentence_count,
                "ai_ratio_pct": round((ai_sentence_count / max(len(sentence_analysis), 1)) * 100, 1)
            },
            "statistics": stats,
            "readability": {
                "flesch_reading_ease": linguistic["flesch_reading_ease"],
                "flesch_kincaid_grade": linguistic["flesch_kincaid_grade"],
                "grade_level_label": linguistic["grade_level_label"],
                "reading_time_seconds": linguistic["reading_time_seconds"]
            },
            "stylometrics": {
                "simpsons_diversity": linguistic["simpsons_diversity"],
                "binoculars_contrast": linguistic["binoculars_contrast"],
                "genre_tone": linguistic["genre_tone"]
            },
            "evasion_audit": evasion_audit
        }


# Global singleton
model_service = ModelService()
