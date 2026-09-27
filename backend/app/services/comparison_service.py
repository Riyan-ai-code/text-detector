from typing import Dict, Any
from backend.app.services.statistical_analyzer import StatisticalAnalyzer
from backend.app.services.stylometric_analyzer import StylometricAnalyzer
from backend.app.services.fingerprint_analyzer import FingerprintAnalyzer
from backend.app.services.authorship_segmenter import AuthorshipSegmenter


class ComparisonService:
    """
    Document Comparison Engine:
    Performs side-by-side forensic analysis of Document A vs. Document B,
    evaluating divergence in AI probability, vocabulary diversity, burstiness,
    syntactic complexity, and authorial style.
    """

    @classmethod
    def compare(cls, doc_a: str, doc_b: str, model_service=None) -> Dict[str, Any]:
        stat_a = StatisticalAnalyzer.analyze(doc_a)
        stylo_a = StylometricAnalyzer.analyze(doc_a)
        fp_a = FingerprintAnalyzer.analyze(doc_a)

        stat_b = StatisticalAnalyzer.analyze(doc_b)
        stylo_b = StylometricAnalyzer.analyze(doc_b)
        fp_b = FingerprintAnalyzer.analyze(doc_b)

        # AI Probability
        prob_a = 50.0
        prob_b = 50.0
        if model_service:
            try:
                res_a = model_service.analyze_full(doc_a)
                res_b = model_service.analyze_full(doc_b)
                prob_a = round(res_a["confidence"] * 100, 1) if "AI" in res_a["prediction"] else round((1.0 - res_a["confidence"]) * 100, 1)
                prob_b = round(res_b["confidence"] * 100, 1) if "AI" in res_b["prediction"] else round((1.0 - res_b["confidence"]) * 100, 1)
            except Exception:
                pass

        vocab_a = stat_a["vocabulary_diversity"]["type_token_ratio"]
        vocab_b = stat_b["vocabulary_diversity"]["type_token_ratio"]

        burst_a = round(stat_a["burstiness"]["burstiness_index"] / 100.0, 2)
        burst_b = round(stat_b["burstiness"]["burstiness_index"] / 100.0, 2)

        # Style deviation between the two documents
        deviation = round(abs(burst_a - burst_b) * 40.0 + abs(vocab_a - vocab_b) * 40.0 + abs(stylo_a["average_sentence_length"] - stylo_b["average_sentence_length"]) * 2.0, 1)
        deviation = min(95.0, max(5.0, deviation))

        divergence_insights = []
        if abs(prob_a - prob_b) >= 25.0:
            higher = "Document A" if prob_a > prob_b else "Document B"
            divergence_insights.append(
                f"{higher} exhibits significantly stronger AI-like predictability and formulaic structural patterns."
            )
        if abs(burst_a - burst_b) >= 0.25:
            divergence_insights.append(
                f"Sentence length cadence diverges markedly: {'Document A' if burst_a > burst_b else 'Document B'} has more natural human-like variation."
            )
        if abs(vocab_a - vocab_b) >= 0.15:
            divergence_insights.append(
                f"Vocabulary richness is notably higher in {'Document A' if vocab_a > vocab_b else 'Document B'}."
            )

        return {
            "document_a": {
                "word_count": stat_a["counts"]["word_count"],
                "sentence_count": stat_a["counts"]["sentence_count"],
                "ai_like_pct": prob_a,
                "vocabulary_diversity": vocab_a,
                "burstiness": burst_a,
                "style_deviation_pct": round(deviation * 0.4, 1),
                "avg_sentence_length": stylo_a["average_sentence_length"],
                "passive_voice_pct": stylo_a["voice_distribution"]["passive_percentage"],
                "cliches_detected": fp_a["cliche_analysis"]["total_cliches_detected"]
            },
            "document_b": {
                "word_count": stat_b["counts"]["word_count"],
                "sentence_count": stat_b["counts"]["sentence_count"],
                "ai_like_pct": prob_b,
                "vocabulary_diversity": vocab_b,
                "burstiness": burst_b,
                "style_deviation_pct": round(deviation, 1),
                "avg_sentence_length": stylo_b["average_sentence_length"],
                "passive_voice_pct": stylo_b["voice_distribution"]["passive_percentage"],
                "cliches_detected": fp_b["cliche_analysis"]["total_cliches_detected"]
            },
            "divergence_score": deviation,
            "divergence_insights": divergence_insights if divergence_insights else ["Both documents exhibit similar stylistic distributions and length patterns."]
        }
