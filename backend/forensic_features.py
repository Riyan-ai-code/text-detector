import re
import math
import unicodedata
from collections import Counter
from typing import Dict, Any, List, Tuple
import numpy as np


class ForensicFeatureExtractor:
    """
    Part 1 Hypothesis Discovery & Feature Extractor:
    Computes fine-grained statistical, stylometric, and punctuation features
    across 26 distinct authorship dimensions.
    """

    # Common discourse transition markers
    TRANSITION_MARKERS = {
        "furthermore", "moreover", "in conclusion", "additionally", "consequently",
        "nevertheless", "on the other hand", "specifically", "for instance",
        "in particular", "notably", "significantly", "as a result", "hence",
        "thus", "to summarize", "in essence", "conversely", "meanwhile", "therefore"
    }

    # Core function words (Pronouns, Prepositions, Conjunctions, Auxiliaries)
    FUNCTION_WORDS = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it",
        "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but",
        "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will",
        "my", "one", "all", "would", "there", "their", "what", "so", "up", "out",
        "if", "about", "who", "get", "which", "go", "me", "when", "make", "can",
        "like", "time", "no", "just", "him", "know", "take", "people", "into",
        "year", "your", "good", "some", "could", "them", "see", "other", "than",
        "then", "now", "look", "only", "come", "its", "over", "think", "also",
        "back", "after", "use", "two", "how", "our", "work", "first", "well",
        "way", "even", "new", "want", "because", "any", "these", "give", "day",
        "most", "us"
    }

    @classmethod
    def extract_all(cls, text: str) -> Dict[str, Any]:
        """Runs the full 26-dimension feature extraction pipeline."""
        if not text or not text.strip():
            return cls._empty_feature_vector()

        raw_text = text
        normalized_text = unicodedata.normalize("NFC", raw_text)

        words = re.findall(r"\b[\w'-]+\b", normalized_text)
        word_count = max(len(words), 1)
        lower_words = [w.lower() for w in words]

        # 1. Punctuation & Unicode Dash Dissection
        punct_features = cls._extract_punctuation_features(raw_text, word_count)

        # 2. Sentence & Paragraph Distributions
        structural_features = cls._extract_structural_distributions(raw_text, words)

        # 3. Vocabulary Diversity & Information Theory
        lexical_features = cls._extract_lexical_information(lower_words)

        # 4. Function Words & Syntactic Repetition
        syntax_features = cls._extract_syntax_and_discourse(raw_text, lower_words, word_count)

        # 5. Formatting, Capitalization & Surface Variations
        surface_features = cls._extract_surface_features(raw_text, words)

        return {
            "summary": {
                "total_words": len(words),
                "total_chars": len(raw_text),
                "total_sentences": structural_features["sentence_count"],
                "total_paragraphs": structural_features["paragraph_count"]
            },
            "punctuation_and_dashes": punct_features,
            "structural_distributions": structural_features,
            "lexical_information": lexical_features,
            "syntax_and_discourse": syntax_features,
            "surface_and_formatting": surface_features
        }

    @classmethod
    def _extract_punctuation_features(cls, text: str, word_count: int) -> Dict[str, Any]:
        """Analyzes exact Unicode hyphen/dash code points and punctuation densities."""
        scale = 1000.0 / word_count

        # Unicode Code Points
        ascii_hyphen_count = text.count("-")          # U+002D
        en_dash_count = text.count("\u2013")         # U+2013 (–)
        em_dash_count = text.count("\u2014")         # U+2014 (—)
        non_breaking_hyphen = text.count("\u2011")   # U+2011
        total_dashes = ascii_hyphen_count + en_dash_count + em_dash_count + non_breaking_hyphen

        # Hyphenated compounds (e.g. state-of-the-art, fine-tuned)
        hyphenated_compounds = len(re.findall(r"\b\w+(?:-\w+)+\b", text))

        # Dash spacing patterns (spaced vs unspaced em/en dashes)
        spaced_em_dashes = len(re.findall(r"\s+\u2014\s+", text))
        unspaced_em_dashes = len(re.findall(r"\w\u2014\w", text))
        spaced_en_dashes = len(re.findall(r"\s+\u2013\s+", text))
        unspaced_en_dashes = len(re.findall(r"\w\u2013\w", text))

        # Standard punctuation frequencies
        commas = text.count(",")
        semicolons = text.count(";")
        colons = text.count(":")
        ellipses = len(re.findall(r"\.{3}|\u2026", text))
        parentheses_pairs = min(text.count("("), text.count(")"))
        
        # Quotation mark types
        ascii_double_quotes = text.count('"')
        unicode_curly_quotes = text.count("“") + text.count("”")
        ascii_single_quotes = text.count("'")
        unicode_single_quotes = text.count("‘") + text.count("’")

        # Repetitive punctuation sequences (e.g. "??", "!!", "--", "?!")
        punct_sequences = len(re.findall(r"[\?!,\.\-;:]{2,}", text))

        return {
            "dash_metrics": {
                "ascii_hyphen_per_1k": round(ascii_hyphen_count * scale, 2),
                "en_dash_per_1k": round(en_dash_count * scale, 2),
                "em_dash_per_1k": round(em_dash_count * scale, 2),
                "total_dashes_count": total_dashes,
                "hyphenated_compounds_count": hyphenated_compounds,
                "em_dash_spacing_profile": {
                    "unspaced_count (word—word)": unspaced_em_dashes,
                    "spaced_count (word — word)": spaced_em_dashes
                },
                "en_dash_spacing_profile": {
                    "unspaced_count": unspaced_en_dashes,
                    "spaced_count": spaced_en_dashes
                }
            },
            "punctuation_densities_per_1k": {
                "commas": round(commas * scale, 2),
                "semicolons": round(semicolons * scale, 2),
                "colons": round(colons * scale, 2),
                "parentheses_pairs": round(parentheses_pairs * scale, 2),
                "ellipses": round(ellipses * scale, 2)
            },
            "quotation_style": {
                "ascii_quotes_ratio": round((ascii_double_quotes + ascii_single_quotes) / max(1, (ascii_double_quotes + ascii_single_quotes + unicode_curly_quotes + unicode_single_quotes)), 2),
                "unicode_curly_quotes_count": unicode_curly_quotes + unicode_single_quotes
            },
            "punctuation_sequence_anomaly_count": punct_sequences
        }

    @classmethod
    def _extract_structural_distributions(cls, text: str, words: List[str]) -> Dict[str, Any]:
        """Calculates sentence and paragraph length statistical distributions."""
        raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        paragraph_count = max(len(raw_paragraphs), 1)

        raw_sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        sentence_count = max(len(raw_sentences), 1)

        # Word counts per sentence
        sent_lengths = [len(re.findall(r"\b\w+\b", s)) for s in raw_sentences]
        if not sent_lengths:
            sent_lengths = [len(words)]

        sent_arr = np.array(sent_lengths, dtype=float)
        mean_sent_len = float(np.mean(sent_arr))
        std_sent_len = float(np.std(sent_arr))
        min_sent_len = int(np.min(sent_arr))
        max_sent_len = int(np.max(sent_arr))

        # Sentence length skewness (asymmetry in human vs uniform AI)
        if len(sent_arr) > 2 and std_sent_len > 1e-6:
            try:
                skewness = float(np.mean(((sent_arr - mean_sent_len) / std_sent_len) ** 3))
            except Exception:
                skewness = 0.0
        else:
            skewness = 0.0

        # Paragraph length distributions (sentences per paragraph)
        para_sent_counts = [len([s for s in re.split(r"[.!?]+", p) if s.strip()]) for p in raw_paragraphs]
        mean_para_len = float(np.mean(para_sent_counts)) if para_sent_counts else 1.0

        return {
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "sentence_length": {
                "mean_words": round(mean_sent_len, 2),
                "std_deviation": round(std_sent_len, 2),
                "burstiness_index": round((std_sent_len / max(1e-5, mean_sent_len)) * 100, 2),
                "min_words": min_sent_len,
                "max_words": max_sent_len,
                "length_skewness": round(skewness, 2)
            },
            "paragraph_length": {
                "mean_sentences_per_para": round(mean_para_len, 2)
            }
        }

    @classmethod
    def _extract_lexical_information(cls, lower_words: List[str]) -> Dict[str, Any]:
        """Calculates Type-Token Ratio, Hapax Legomena, Yule's K, and Shannon Entropy."""
        n = len(lower_words)
        if n == 0:
            return {"ttr": 0.0, "hapax_ratio": 0.0, "yules_k": 0.0, "shannon_entropy": 0.0}

        counts = Counter(lower_words)
        v = len(counts)

        # 1. Type-Token Ratio (TTR)
        ttr = (v / n) * 100.0

        # 2. Hapax Legomena (Words appearing exactly once)
        hapax_count = sum(1 for count in counts.values() if count == 1)
        hapax_ratio = (hapax_count / v) * 100.0 if v > 0 else 0.0

        # 3. Yule's Characteristic K (Length-independent vocabulary richness)
        # K = 10^4 * (sum(f_i * i^2) - N) / N^2
        freq_spectrum = Counter(counts.values())
        sum_spectrum = sum(f_m * (m ** 2) for m, f_m in freq_spectrum.items())
        yules_k = 10000.0 * (sum_spectrum - n) / (n ** 2) if n > 1 else 0.0

        # 4. Shannon Lexical Entropy
        entropy = 0.0
        for count in counts.values():
            p = count / n
            entropy -= p * math.log2(p)

        return {
            "vocabulary_diversity_ttr": round(ttr, 2),
            "hapax_legomena_ratio": round(hapax_ratio, 2),
            "yules_characteristic_k": round(max(0.0, yules_k), 2),
            "shannon_lexical_entropy": round(entropy, 2)
        }

    @classmethod
    def _extract_syntax_and_discourse(cls, text: str, lower_words: List[str], word_count: int) -> Dict[str, Any]:
        """Analyzes function words, discourse transition density, and n-gram repetition."""
        scale = 1000.0 / word_count

        # Function word density
        func_word_count = sum(1 for w in lower_words if w in cls.FUNCTION_WORDS)
        func_word_ratio = (func_word_count / word_count) * 100.0

        # Discourse transition markers
        lower_text = text.lower()
        transition_matches = 0
        for marker in cls.TRANSITION_MARKERS:
            pattern = r"\b" + re.escape(marker) + r"\b"
            transition_matches += len(re.findall(pattern, lower_text))

        # Repeated 3-grams (Phrase reuse index)
        trigrams = [tuple(lower_words[i:i+3]) for i in range(len(lower_words) - 2)]
        trigram_counts = Counter(trigrams)
        repeated_trigrams = sum(count for count in trigram_counts.values() if count > 1)
        phrase_reuse_index = (repeated_trigrams / max(1, len(trigrams))) * 100.0 if trigrams else 0.0

        return {
            "function_word_ratio_pct": round(func_word_ratio, 2),
            "discourse_transitions_per_1k": round(transition_matches * scale, 2),
            "phrase_reuse_trigram_pct": round(phrase_reuse_index, 2)
        }

    @classmethod
    def _extract_surface_features(cls, text: str, words: List[str]) -> Dict[str, Any]:
        """Measures casing regularity, capitalization density, and formatting anomalies."""
        word_count = max(len(words), 1)
        uppercase_words = sum(1 for w in words if w.isupper() and len(w) > 1)
        titlecase_words = sum(1 for w in words if w.istitle())

        return {
            "all_caps_word_density_pct": round((uppercase_words / word_count) * 100, 2),
            "title_cased_word_ratio_pct": round((titlecase_words / word_count) * 100, 2),
            "has_trailing_whitespace": bool(re.search(r"[ \t]+$", text, re.MULTILINE))
        }

    @classmethod
    def _empty_feature_vector(cls) -> Dict[str, Any]:
        return {
            "summary": {"total_words": 0, "total_chars": 0, "total_sentences": 0, "total_paragraphs": 0},
            "punctuation_and_dashes": {},
            "structural_distributions": {},
            "lexical_information": {},
            "syntax_and_discourse": {},
            "surface_and_formatting": {}
        }
