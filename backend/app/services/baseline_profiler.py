import re
import math
from collections import Counter
from typing import Dict, Any, List
from backend.app.services.statistical_analyzer import StatisticalAnalyzer
from backend.app.services.stylometric_analyzer import StylometricAnalyzer


class BaselineProfiler:
    """
    Personal Writing Fingerprint Baseline & Author Profiler Engine:
    Analyzes 3-5 genuine writing samples to create an authorial fingerprint,
    and compares new documents against this baseline to calculate style deviation
    and explain dimensional shifts.
    """

    @classmethod
    def create_baseline(cls, samples: List[str], profile_name: str = "Primary Baseline") -> Dict[str, Any]:
        valid_samples = [s.strip() for s in samples if s and len(s.strip().split()) >= 15]
        if not valid_samples:
            return cls._empty_baseline(profile_name)

        combined_text = "\n\n".join(valid_samples)
        stat = StatisticalAnalyzer.analyze(combined_text)
        stylo = StylometricAnalyzer.analyze(combined_text)

        all_words = re.findall(r"\b[\w'-]+\b", combined_text.lower())
        bigrams = [f"{all_words[i]} {all_words[i+1]}" for i in range(len(all_words) - 1)]
        common_phrases = [
            {"phrase": p, "count": c}
            for p, c in Counter(bigrams).most_common(8)
            if c >= 2
        ]

        return {
            "profile_name": profile_name,
            "sample_count": len(valid_samples),
            "total_words": stat["counts"]["word_count"],
            "metrics": {
                "avg_sentence_length": stylo["average_sentence_length"],
                "sentence_length_std": stat["burstiness"]["std_sentence_length"],
                "burstiness_index": stat["burstiness"]["burstiness_index"],
                "type_token_ratio": stat["vocabulary_diversity"]["type_token_ratio"],
                "simpsons_diversity": stat["vocabulary_diversity"]["simpsons_diversity_index"],
                "clauses_per_sentence": stylo["sentence_complexity"]["average_clauses_per_sentence"],
                "passive_voice_pct": stylo["voice_distribution"]["passive_percentage"],
                "function_word_ratio": stylo["lexical_distribution"]["function_word_ratio"],
                "punctuation_per_100": stat["punctuation_distribution"]["ratios_per_100_words"],
                "first_person_pct": stylo["pronoun_usage"]["first_person_pct"],
                "words_per_paragraph": stylo["paragraph_structure"]["average_words_per_paragraph"]
            },
            "common_phrases": common_phrases,
            "created_at": "2026-09-22"
        }

    @classmethod
    def compare_to_baseline(cls, text: str, baseline: Dict[str, Any]) -> Dict[str, Any]:
        if not text or not text.strip() or not baseline or not baseline.get("metrics"):
            return {
                "has_baseline": False,
                "style_similarity_pct": 0,
                "style_deviation_pct": 0,
                "shift_explanations": ["No active personal baseline loaded."],
                "dimension_comparisons": []
            }

        target_stat = StatisticalAnalyzer.analyze(text)
        target_stylo = StylometricAnalyzer.analyze(text)

        b_metrics = baseline["metrics"]
        shifts = []
        dimensions = []
        similarity_points = 100.0

        # 1. Sentence Length Comparison
        base_sent_len = b_metrics.get("avg_sentence_length", 15.0)
        curr_sent_len = target_stylo["average_sentence_length"]
        len_diff = abs(curr_sent_len - base_sent_len)
        len_penalty = min(25.0, (len_diff / max(base_sent_len, 1)) * 30.0)
        similarity_points -= len_penalty
        dimensions.append({
            "dimension": "Average Sentence Length",
            "baseline_val": f"{base_sent_len:.1f} words",
            "current_val": f"{curr_sent_len:.1f} words",
            "deviation": f"{'+' if curr_sent_len > base_sent_len else ''}{curr_sent_len - base_sent_len:.1f} words"
        })
        if len_diff >= 6.0:
            shifts.append(
                f"Sentence length shifted from your usual {base_sent_len:.1f} words to {curr_sent_len:.1f} words ({'longer, more complex phrasing' if curr_sent_len > base_sent_len else 'shorter, staccato rhythm'})."
            )

        # 2. Burstiness / Cadence Comparison
        base_burst = b_metrics.get("burstiness_index", 50.0)
        curr_burst = target_stat["burstiness"]["burstiness_index"]
        burst_diff = abs(curr_burst - base_burst)
        burst_penalty = min(20.0, (burst_diff / 100.0) * 25.0)
        similarity_points -= burst_penalty
        dimensions.append({
            "dimension": "Sentence-Length Variation (Burstiness)",
            "baseline_val": f"{base_burst:.1f}/100",
            "current_val": f"{curr_burst:.1f}/100",
            "deviation": f"{'+' if curr_burst > base_burst else ''}{curr_burst - base_burst:.1f}"
        })
        if curr_burst < base_burst - 20.0:
            shifts.append(
                f"Sentence cadence is significantly more uniform than your usual baseline ({curr_burst:.1f} vs your baseline {base_burst:.1f})."
            )

        # 3. Vocabulary Diversity Comparison
        base_ttr = b_metrics.get("type_token_ratio", 0.60)
        curr_ttr = target_stat["vocabulary_diversity"]["type_token_ratio"]
        ttr_diff = abs(curr_ttr - base_ttr)
        ttr_penalty = min(20.0, (ttr_diff / max(base_ttr, 0.1)) * 25.0)
        similarity_points -= ttr_penalty
        dimensions.append({
            "dimension": "Vocabulary Diversity (TTR)",
            "baseline_val": f"{base_ttr:.3f}",
            "current_val": f"{curr_ttr:.3f}",
            "deviation": f"{'+' if curr_ttr > base_ttr else ''}{curr_ttr - base_ttr:.3f}"
        })
        if ttr_diff >= 0.15:
            shifts.append(
                f"Vocabulary richness deviates from your typical baseline ({'richer lexicon' if curr_ttr > base_ttr else 'more repetitive vocabulary'})."
            )

        # 4. Passive Voice Comparison
        base_pass = b_metrics.get("passive_voice_pct", 10.0)
        curr_pass = target_stylo["voice_distribution"]["passive_percentage"]
        pass_diff = abs(curr_pass - base_pass)
        pass_penalty = min(15.0, (pass_diff / 100.0) * 20.0)
        similarity_points -= pass_penalty
        dimensions.append({
            "dimension": "Passive Voice Density",
            "baseline_val": f"{base_pass:.1f}%",
            "current_val": f"{curr_pass:.1f}%",
            "deviation": f"{'+' if curr_pass > base_pass else ''}{curr_pass - base_pass:.1f}%"
        })
        if curr_pass >= base_pass + 25.0:
            shifts.append(
                f"Passive voice usage increased abruptly ({curr_pass:.1f}% vs your baseline {base_pass:.1f}%)."
            )

        # 5. Punctuation Habits (Em-dash, semicolon)
        base_punct = b_metrics.get("punctuation_per_100", {})
        curr_punct = target_stat["punctuation_distribution"].get("ratios_per_100_words", {})
        base_dash = base_punct.get("em_dash_per_100_words", 0.0)
        curr_dash = curr_punct.get("em_dash_per_100_words", 0.0)
        if abs(curr_dash - base_dash) >= 1.5:
            shifts.append(
                f"Em-dash punctuation habit diverged from baseline ({curr_dash:.1f} vs baseline {base_dash:.1f} per 100 words)."
            )

        # Clamp scores
        similarity_pct = round(max(15.0, min(95.0, similarity_points)), 1)
        deviation_pct = round(100.0 - similarity_pct, 1)

        if not shifts:
            shifts.append("Writing matches your established personal baseline across all major stylistic and structural dimensions.")

        return {
            "has_baseline": True,
            "profile_name": baseline.get("profile_name", "Primary Baseline"),
            "style_similarity_pct": similarity_pct,
            "style_deviation_pct": deviation_pct,
            "similarity_bar": cls._generate_ascii_bar(similarity_pct),
            "deviation_bar": cls._generate_ascii_bar(deviation_pct),
            "shift_explanations": shifts,
            "dimension_comparisons": dimensions
        }

    @staticmethod
    def _generate_ascii_bar(pct: float) -> str:
        total_blocks = 10
        filled = int(round((pct / 100.0) * total_blocks))
        filled = max(0, min(total_blocks, filled))
        return "█" * filled + "░" * (total_blocks - filled)

    @classmethod
    def _empty_baseline(cls, profile_name: str) -> Dict[str, Any]:
        return {
            "profile_name": profile_name,
            "sample_count": 0,
            "total_words": 0,
            "metrics": {},
            "common_phrases": [],
            "created_at": None
        }
