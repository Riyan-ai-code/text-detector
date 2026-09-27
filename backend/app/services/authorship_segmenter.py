import re
from typing import Dict, Any, List


class AuthorshipSegmenter:
    """
    Mixed Authorship Segmentation & Timeline Engine:
    Analyzes paragraph-by-paragraph and section transitions to identify
    co-written documents, mixed authorship, and abrupt stylistic boundaries.
    """

    TRANSITION_DELTA_THRESHOLD = 0.25  # Shift of 25% or more indicates a transition

    @classmethod
    def segment(cls, text: str, model_service=None) -> Dict[str, Any]:
        if not text or not text.strip():
            return cls._empty_result()

        raw_text = text.strip()
        # Split by paragraph breaks (double newline or single indented newline)
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", raw_text) if p.strip()]
        
        # If single paragraph, attempt to split by multi-sentence logical chunks (every 3-4 sentences)
        if len(paragraphs) == 1 and len(raw_text.split()) >= 60:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw_text) if s.strip()]
            if len(sentences) >= 4:
                chunk_size = max(2, len(sentences) // 3)
                paragraphs = [
                    " ".join(sentences[i : i + chunk_size])
                    for i in range(0, len(sentences), chunk_size)
                ]

        if not paragraphs:
            paragraphs = [raw_text]

        block_results = []
        for idx, p in enumerate(paragraphs):
            p_words = re.findall(r"\b[\w'-]+\b", p)
            w_count = len(p_words)
            p_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
            s_count = max(len(p_sentences), 1)

            # Analyze paragraph block
            prob, conf, signals = cls._score_block(p, p_words, s_count, model_service)

            if prob >= 0.60:
                classification = "AI-like"
                status_color = "red"
            elif prob <= 0.40:
                classification = "Human-like"
                status_color = "green"
            else:
                classification = "Mixed / Uncertain"
                status_color = "yellow"

            block_results.append({
                "block_index": idx + 1,
                "label": f"Paragraph {idx + 1}",
                "text_snippet": p[:140] + ("..." if len(p) > 140 else ""),
                "full_text": p,
                "word_count": w_count,
                "sentence_count": s_count,
                "ai_probability": round(prob * 100, 1),
                "human_probability": round((1.0 - prob) * 100, 1),
                "classification": classification,
                "status_color": status_color,
                "confidence": conf,
                "signals": signals
            })

        # Detect Transition Points
        transitions = []
        for i in range(len(block_results) - 1):
            curr_b = block_results[i]
            next_b = block_results[i + 1]
            prob_diff = round(next_b["ai_probability"] - curr_b["ai_probability"], 1)

            if curr_b["classification"] != next_b["classification"] or abs(prob_diff) >= (cls.TRANSITION_DELTA_THRESHOLD * 100):
                direction = (
                    f"{curr_b['classification']} → {next_b['classification']}"
                )
                transitions.append({
                    "from_block": curr_b["block_index"],
                    "to_block": next_b["block_index"],
                    "from_label": curr_b["label"],
                    "to_label": next_b["label"],
                    "direction": direction,
                    "delta_probability": prob_diff,
                    "severity": "HIGH" if abs(prob_diff) >= 40.0 else "MEDIUM",
                    "explanation": (
                        f"Abrupt stylistic shift from {curr_b['label']} ({curr_b['classification']}) to "
                        f"{next_b['label']} ({next_b['classification']}) with a {abs(prob_diff)}% probability delta."
                    )
                })

        # Calculate Overall Authorship Distribution
        total_blocks = len(block_results)
        ai_blocks = sum(1 for b in block_results if b["classification"] == "AI-like")
        human_blocks = sum(1 for b in block_results if b["classification"] == "Human-like")
        mixed_blocks = sum(1 for b in block_results if b["classification"] == "Mixed / Uncertain")

        is_mixed = len(transitions) > 0 or (ai_blocks > 0 and human_blocks > 0)

        summary_text = (
            f"Detected {len(transitions)} authorship transition point{'s' if len(transitions) != 1 else ''}: "
            + "; ".join(f"{t['from_label']} → {t['to_label']} ({t['direction']})" for t in transitions)
            if transitions else
            f"Consistent {block_results[0]['classification']} patterns across all {total_blocks} paragraph{'s' if total_blocks != 1 else ''} with no detected transition boundaries."
            if block_results else "No text segments analyzed."
        )

        return {
            "is_mixed_authorship": is_mixed,
            "total_blocks": total_blocks,
            "blocks": block_results,
            "transitions_count": len(transitions),
            "transitions": transitions,
            "distribution": {
                "human_blocks_pct": round((human_blocks / max(total_blocks, 1)) * 100, 1),
                "mixed_blocks_pct": round((mixed_blocks / max(total_blocks, 1)) * 100, 1),
                "ai_blocks_pct": round((ai_blocks / max(total_blocks, 1)) * 100, 1)
            },
            "summary": summary_text
        }

    @classmethod
    def _score_block(cls, text: str, words: List[str], sentence_count: int, model_service=None) -> tuple:
        """Computes AI probability, confidence, and contributing signals for an individual paragraph."""
        signals = []
        w_count = max(len(words), 1)

        # 1. Model prediction if available
        raw_prob = None
        if model_service is not None and hasattr(model_service, "predict_model_1"):
            try:
                m1 = model_service.predict_model_1(text)
                raw_prob = m1["confidence"] if "AI" in m1["prediction"] else (1.0 - m1["confidence"])
            except Exception:
                raw_prob = None

        # 2. Stylometric heuristics
        from backend.model_service import LinguisticAnalyzer
        metrics = LinguisticAnalyzer.analyze(text)
        b_score = metrics.get("burstiness", 50.0)
        p_score = metrics.get("perplexity", 50.0)
        lex_score = metrics.get("lexical", 50.0)

        # Approximate block AI score
        heuristic_prob = (
            (1.0 - (b_score / 100.0)) * 0.35 +
            (1.0 - (p_score / 100.0)) * 0.30 +
            (1.0 - (lex_score / 100.0)) * 0.20 +
            (min(5.0, len(words) / max(sentence_count, 1) / 15.0)) * 0.15
        )

        if raw_prob is not None:
            final_prob = 0.60 * raw_prob + 0.40 * heuristic_prob
        else:
            final_prob = heuristic_prob

        final_prob = max(0.05, min(0.95, final_prob))

        # Signals
        if p_score < 40.0:
            signals.append("High predictability")
        elif p_score > 65.0:
            signals.append("High lexical surprise")

        if b_score < 35.0:
            signals.append("Low sentence-length variation")
        elif b_score > 65.0:
            signals.append("High burstiness variation")

        if lex_score < 45.0:
            signals.append("Low vocabulary variation")
        elif lex_score > 75.0:
            signals.append("Rich vocabulary diversity")

        # Confidence
        if w_count < 25:
            conf = "LOW"
        elif 0.35 <= final_prob <= 0.65:
            conf = "MEDIUM"
        else:
            conf = "HIGH"

        return final_prob, conf, signals

    @classmethod
    def _empty_result(cls) -> Dict[str, Any]:
        return {
            "is_mixed_authorship": False,
            "total_blocks": 0,
            "blocks": [],
            "transitions_count": 0,
            "transitions": [],
            "distribution": {"human_blocks_pct": 0.0, "mixed_blocks_pct": 0.0, "ai_blocks_pct": 0.0},
            "summary": "No segments available."
        }
