import re
import math
from collections import Counter
from typing import Dict, Any, List


class StatisticalAnalyzer:
    """
    Forensic Statistical Signal Engine:
    Measures perplexity, burstiness, distributions, vocabulary entropy,
    n-gram repetition, and punctuation profiles.
    """

    PUNCTUATION_PATTERNS = {
        "comma": r",",
        "period": r"\.",
        "semicolon": r";",
        "colon": r":",
        "em_dash": r"[—–]|--",
        "hyphen": r"-",
        "exclamation": r"!",
        "question": r"\?",
        "quotes": r'["\'""]',
        "parentheses": r"[\(\)\[\]\{\}]"
    }

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return cls._empty_result()

        raw_text = text.strip()
        
        # 1. Tokenization
        words = re.findall(r"\b[\w'-]+\b", raw_text)
        word_count = len(words)
        lower_words = [w.lower() for w in words]
        
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw_text) if s.strip()]
        if not raw_sentences:
            raw_sentences = [raw_text]
        sentence_count = len(raw_sentences)

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_text) if p.strip()]
        paragraph_count = max(len(paragraphs), 1)

        # 2. Sentence Length Distribution
        sentence_lengths = [len(re.findall(r"\b[\w'-]+\b", s)) for s in raw_sentences]
        sentence_lengths = [l for l in sentence_lengths if l > 0] or [word_count]
        
        mean_sent_len = sum(sentence_lengths) / len(sentence_lengths)
        variance_sent_len = sum((l - mean_sent_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        std_sent_len = math.sqrt(variance_sent_len)
        min_sent_len = min(sentence_lengths)
        max_sent_len = max(sentence_lengths)
        sorted_lens = sorted(sentence_lengths)
        median_sent_len = sorted_lens[len(sorted_lens) // 2]

        # 3. Burstiness Index
        # Coefficient of variation (CV = std / mean), normalized 0-100
        # AI text typically has low burstiness (uniform lengths, CV < 0.3)
        # Human text typically has high burstiness (spiky, CV > 0.6)
        cv = (std_sent_len / mean_sent_len) if mean_sent_len > 0 else 0.0
        burstiness_score = round(min(100.0, cv * 100.0), 1)

        # 4. Word Length Distribution & Syllables
        word_lengths = [len(w) for w in words] if words else [0]
        avg_word_len = round(sum(word_lengths) / len(word_lengths), 2) if word_lengths else 0.0
        
        word_len_bins = {
            "short_1_3": sum(1 for l in word_lengths if 1 <= l <= 3),
            "medium_4_6": sum(1 for l in word_lengths if 4 <= l <= 6),
            "long_7_9": sum(1 for l in word_lengths if 7 <= l <= 9),
            "very_long_10_plus": sum(1 for l in word_lengths if l >= 10)
        }

        # 5. Vocabulary Diversity (TTR, Root TTR, Simpson's D, Shannon Entropy)
        vocab = Counter(lower_words)
        unique_words = len(vocab)
        ttr = round(unique_words / word_count, 4) if word_count > 0 else 0.0
        root_ttr = round(unique_words / math.sqrt(word_count), 4) if word_count > 0 else 0.0

        # Simpson's Diversity Index: D = 1 - sum(n*(n-1) / (N*(N-1)))
        if word_count > 1:
            simpsons_sum = sum(cnt * (cnt - 1) for cnt in vocab.values())
            simpsons_d = round(1.0 - (simpsons_sum / (word_count * (word_count - 1))), 4)
        else:
            simpsons_d = 1.0

        # Shannon Entropy H = - sum(p * log2(p))
        entropy = 0.0
        if word_count > 0:
            for count in vocab.values():
                p = count / word_count
                if p > 0:
                    entropy -= p * math.log2(p)
        shannon_entropy = round(entropy, 3)

        # 6. N-gram Repetition Rates
        repetition = cls._calc_ngram_repetitions(lower_words)

        # 7. Punctuation Profile
        punct_profile = cls._calc_punctuation_distribution(raw_text, word_count)

        # 8. Perplexity / Predictability Estimation
        # LLMs generate text in narrow perplexity bands; estimate cross-entropy based on character n-grams and vocabulary entropy
        char_counts = Counter(raw_text.lower())
        total_chars = max(len(raw_text), 1)
        char_entropy = -sum((cnt / total_chars) * math.log2(cnt / total_chars) for cnt in char_counts.values() if cnt > 0)
        
        # Predictability index (0-100, where higher means more predictable/machine-like)
        # Low burstiness + low entropy + high n-gram repetition = higher predictability
        pred_signal = (
            (100.0 - burstiness_score) * 0.35 +
            (repetition.get("bigram_repeat_rate_pct", 0) * 1.5) * 0.20 +
            (1.0 - min(1.0, ttr)) * 100.0 * 0.25 +
            (1.0 - min(1.0, simpsons_d)) * 100.0 * 0.20
        )
        predictability_score = round(max(5.0, min(95.0, pred_signal)), 1)
        perplexity_estimate = round(max(10.0, min(120.0, 100.0 - predictability_score + (cv * 15))), 1)

        return {
            "counts": {
                "word_count": word_count,
                "character_count": len(raw_text),
                "sentence_count": sentence_count,
                "paragraph_count": paragraph_count
            },
            "perplexity": {
                "estimated_perplexity": perplexity_estimate,
                "predictability_score": predictability_score,
                "shannon_entropy": shannon_entropy,
                "character_entropy": round(char_entropy, 3)
            },
            "burstiness": {
                "burstiness_index": burstiness_score,
                "coefficient_of_variation": round(cv, 3),
                "std_sentence_length": round(std_sent_len, 2),
                "mean_sentence_length": round(mean_sent_len, 2)
            },
            "sentence_length_distribution": {
                "min": min_sent_len,
                "max": max_sent_len,
                "mean": round(mean_sent_len, 2),
                "median": median_sent_len,
                "std_dev": round(std_sent_len, 2),
                "lengths": sentence_lengths[:50]
            },
            "word_length_distribution": {
                "average_word_length": avg_word_len,
                "bins": word_len_bins
            },
            "vocabulary_diversity": {
                "unique_words": unique_words,
                "type_token_ratio": ttr,
                "root_ttr": root_ttr,
                "simpsons_diversity_index": simpsons_d,
                "shannon_entropy": shannon_entropy
            },
            "ngram_repetitions": repetition,
            "punctuation_distribution": punct_profile
        }

    @classmethod
    def _calc_ngram_repetitions(cls, words: List[str]) -> Dict[str, Any]:
        n = len(words)
        if n < 4:
            return {
                "unigram_repeat_rate_pct": 0.0,
                "bigram_repeat_rate_pct": 0.0,
                "trigram_repeat_rate_pct": 0.0,
                "fourgram_repeat_rate_pct": 0.0,
                "repeated_phrases": []
            }

        bigrams = [f"{words[i]} {words[i+1]}" for i in range(n - 1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(n - 2)]
        fourgrams = [f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}" for i in range(n - 3)]

        bi_counts = Counter(bigrams)
        tri_counts = Counter(trigrams)
        four_counts = Counter(fourgrams)

        bi_repeats = sum(cnt - 1 for cnt in bi_counts.values() if cnt > 1)
        tri_repeats = sum(cnt - 1 for cnt in tri_counts.values() if cnt > 1)
        four_repeats = sum(cnt - 1 for cnt in four_counts.values() if cnt > 1)

        bi_rate = round((bi_repeats / max(len(bigrams), 1)) * 100.0, 2)
        tri_rate = round((tri_repeats / max(len(trigrams), 1)) * 100.0, 2)
        four_rate = round((four_repeats / max(len(fourgrams), 1)) * 100.0, 2)

        # Most repeated phrases (min count 2)
        top_repeated = [
            {"phrase": phrase, "count": count}
            for phrase, count in tri_counts.most_common(5)
            if count > 1
        ]

        return {
            "unigram_repeat_rate_pct": round((1.0 - (len(set(words)) / max(n, 1))) * 100.0, 2),
            "bigram_repeat_rate_pct": bi_rate,
            "trigram_repeat_rate_pct": tri_rate,
            "fourgram_repeat_rate_pct": four_rate,
            "repeated_phrases": top_repeated
        }

    @classmethod
    def _calc_punctuation_distribution(cls, text: str, word_count: int) -> Dict[str, Any]:
        counts = {}
        total_marks = 0

        for name, pattern in cls.PUNCTUATION_PATTERNS.items():
            matches = len(re.findall(pattern, text))
            counts[name] = matches
            total_marks += matches

        ratios = {
            f"{k}_per_100_words": round((v / max(word_count, 1)) * 100.0, 2)
            for k, v in counts.items()
        }

        # Em-dash and semicolon habits are strong individual and AI discriminators
        return {
            "counts": counts,
            "total_punctuation_marks": total_marks,
            "punctuation_to_word_ratio": round(total_marks / max(word_count, 1), 3),
            "ratios_per_100_words": ratios
        }

    @classmethod
    def _empty_result(cls) -> Dict[str, Any]:
        return {
            "counts": {"word_count": 0, "character_count": 0, "sentence_count": 0, "paragraph_count": 0},
            "perplexity": {"estimated_perplexity": 50.0, "predictability_score": 50.0, "shannon_entropy": 0.0, "character_entropy": 0.0},
            "burstiness": {"burstiness_index": 50.0, "coefficient_of_variation": 0.0, "std_sentence_length": 0.0, "mean_sentence_length": 0.0},
            "sentence_length_distribution": {"min": 0, "max": 0, "mean": 0.0, "median": 0, "std_dev": 0.0, "lengths": []},
            "word_length_distribution": {"average_word_length": 0.0, "bins": {}},
            "vocabulary_diversity": {"unique_words": 0, "type_token_ratio": 0.0, "root_ttr": 0.0, "simpsons_diversity_index": 0.0, "shannon_entropy": 0.0},
            "ngram_repetitions": {"unigram_repeat_rate_pct": 0.0, "bigram_repeat_rate_pct": 0.0, "trigram_repeat_rate_pct": 0.0, "fourgram_repeat_rate_pct": 0.0, "repeated_phrases": []},
            "punctuation_distribution": {"counts": {}, "total_punctuation_marks": 0, "punctuation_to_word_ratio": 0.0, "ratios_per_100_words": {}}
        }
