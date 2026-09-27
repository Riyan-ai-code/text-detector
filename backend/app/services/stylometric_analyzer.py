import re
import math
from collections import Counter
from typing import Dict, Any, List


class StylometricAnalyzer:
    """
    Forensic Stylometric & Syntactic Signal Engine:
    Evaluates sentence complexity, active/passive voice, function word density,
    transition markers, pronoun distribution, and paragraph structural uniformity.
    """

    SUBORDINATE_CONJUNCTIONS = {
        "although", "because", "since", "while", "whereas", "if", "unless",
        "though", "even though", "provided", "assuming", "inasmuch as",
        "in order that", "so that", "lest", "until", "before", "after", "whenever"
    }

    COORDINATE_CONJUNCTIONS = {"and", "but", "or", "nor", "for", "yet", "so"}

    TRANSITION_WORDS = {
        "furthermore", "moreover", "in addition", "additionally", "consequently",
        "nevertheless", "nonetheless", "on the other hand", "specifically",
        "for instance", "for example", "in particular", "notably", "significantly",
        "as a result", "hence", "thus", "therefore", "in conclusion", "to summarize",
        "in essence", "conversely", "meanwhile", "ultimately", "importantly"
    }

    FUNCTION_WORDS = {
        "the", "a", "an", "this", "that", "these", "those", "my", "your", "his",
        "her", "its", "our", "their", "in", "on", "at", "to", "for", "with", "by",
        "from", "about", "into", "through", "after", "over", "between", "out",
        "against", "during", "without", "before", "under", "around", "among",
        "and", "but", "or", "so", "yet", "for", "nor", "because", "although",
        "since", "while", "if", "when", "where", "as", "is", "am", "are", "was",
        "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "shall", "should", "may", "might", "must", "can", "could"
    }

    FIRST_PERSON_SINGULAR = {"i", "me", "my", "mine", "myself"}
    FIRST_PERSON_PLURAL = {"we", "us", "our", "ours", "ourselves"}
    SECOND_PERSON = {"you", "your", "yours", "yourself", "yourselves"}
    THIRD_PERSON = {"he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves"}

    IRREGULAR_PARTICIPLES = {
        "been", "done", "gone", "made", "seen", "taken", "known", "written",
        "given", "found", "built", "held", "shown", "paid", "run", "brought",
        "set", "read", "left", "kept", "begun", "chosen", "drawn", "spoken", "understood"
    }

    BE_VERBS = {"is", "am", "are", "was", "were", "be", "been", "being"}

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return cls._empty_result()

        raw_text = text.strip()
        words = re.findall(r"\b[\w'-]+\b", raw_text)
        word_count = len(words)
        lower_words = [w.lower() for w in words]
        
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw_text) if s.strip()]
        if not raw_sentences:
            raw_sentences = [raw_text]
        sentence_count = len(raw_sentences)

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_text) if p.strip()]
        paragraph_count = max(len(paragraphs), 1)

        # 1. Complexity & Clause Metrics
        complexity = cls._calc_sentence_complexity(raw_sentences, lower_words)

        # 2. Voice Analysis (Active vs Passive)
        voice = cls._detect_voice_distribution(raw_sentences)

        # 3. Function vs Content Word Frequencies
        func_count = sum(1 for w in lower_words if w in cls.FUNCTION_WORDS)
        content_count = max(0, word_count - func_count)
        func_ratio = round(func_count / max(word_count, 1), 3)
        content_ratio = round(content_count / max(word_count, 1), 3)

        # 4. Discourse Transitions
        transitions_found = []
        lower_text = raw_text.lower()
        for marker in cls.TRANSITION_WORDS:
            count = len(re.findall(rf"\b{re.escape(marker)}\b", lower_text))
            if count > 0:
                transitions_found.append({"marker": marker, "count": count})
        total_transitions = sum(t["count"] for t in transitions_found)
        transition_density = round((total_transitions / max(word_count, 1)) * 100.0, 2)

        # 5. Pronoun Usage
        pronouns = cls._calc_pronoun_distribution(lower_words, word_count)

        # 6. Paragraph Structural Uniformity
        paragraph_metrics = cls._calc_paragraph_metrics(paragraphs, raw_sentences)

        # Syntactic score: composite index (0-100) of formal/monotonous sentence structuring
        # AI text often features higher passive voice, higher transition density, and uniform paragraph sizes
        syntax_score = min(100.0, max(0.0, (
            (voice["passive_percentage"] * 0.4) +
            (min(5.0, transition_density) * 8.0) +
            (paragraph_metrics["uniformity_score"] * 0.3) +
            (min(1.0, complexity["subordinate_clause_density"]) * 20.0)
        )))

        return {
            "average_sentence_length": round(word_count / max(sentence_count, 1), 2),
            "sentence_complexity": complexity,
            "voice_distribution": voice,
            "lexical_distribution": {
                "function_words_count": func_count,
                "content_words_count": content_count,
                "function_word_ratio": func_ratio,
                "content_word_ratio": content_ratio
            },
            "discourse_transitions": {
                "total_transitions": total_transitions,
                "transition_density_per_100_words": transition_density,
                "markers_detected": transitions_found
            },
            "pronoun_usage": pronouns,
            "paragraph_structure": paragraph_metrics,
            "syntactic_formality_score": round(syntax_score, 1)
        }

    @classmethod
    def _calc_sentence_complexity(cls, sentences: List[str], lower_words: List[str]) -> Dict[str, Any]:
        sub_count = 0
        coord_count = 0
        clause_counts = []

        for sent in sentences:
            s_words = [w.lower() for w in re.findall(r"\b[\w'-]+\b", sent)]
            sub_in_sent = sum(1 for w in s_words if w in cls.SUBORDINATE_CONJUNCTIONS)
            coord_in_sent = sum(1 for w in s_words if w in cls.COORDINATE_CONJUNCTIONS)
            commas_in_sent = sent.count(",") + sent.count(";")
            
            sub_count += sub_in_sent
            coord_count += coord_in_sent
            
            # Approximate clause depth = main clause (1) + subordinate clauses + coordinate clauses/commas
            depth = 1 + sub_in_sent + (1 if coord_in_sent > 1 else 0) + (1 if commas_in_sent >= 2 else 0)
            clause_counts.append(depth)

        avg_clauses = sum(clause_counts) / max(len(clause_counts), 1)
        
        return {
            "average_clauses_per_sentence": round(avg_clauses, 2),
            "subordinate_conjunctions_count": sub_count,
            "subordinate_clause_density": round((sub_count / max(len(lower_words), 1)) * 100.0, 2),
            "coordinate_conjunctions_count": coord_count,
            "complexity_level": "High" if avg_clauses >= 2.5 else "Moderate" if avg_clauses >= 1.6 else "Simple"
        }

    @classmethod
    def _detect_voice_distribution(cls, sentences: List[str]) -> Dict[str, Any]:
        passive_count = 0
        active_count = 0

        # Pattern: be-verb + optional adverb + past participle (-ed or irregular)
        passive_pattern = re.compile(
            r"\b(is|am|are|was|were|be|been|being)\b\s+(\w+ly\s+)?(\w+ed|" +
            "|".join(cls.IRREGULAR_PARTICIPLES) + r")\b",
            re.IGNORECASE
        )

        for sent in sentences:
            if passive_pattern.search(sent):
                passive_count += 1
            else:
                active_count += 1

        total = max(len(sentences), 1)
        passive_pct = round((passive_count / total) * 100.0, 1)
        active_pct = round((active_count / total) * 100.0, 1)

        return {
            "active_sentences_count": active_count,
            "passive_sentences_count": passive_count,
            "active_percentage": active_pct,
            "passive_percentage": passive_pct,
            "dominant_voice": "Passive" if passive_pct >= 50.0 else "Active"
        }

    @classmethod
    def _calc_pronoun_distribution(cls, words: List[str], total_words: int) -> Dict[str, Any]:
        n = max(total_words, 1)
        first_sing = sum(1 for w in words if w in cls.FIRST_PERSON_SINGULAR)
        first_plur = sum(1 for w in words if w in cls.FIRST_PERSON_PLURAL)
        second = sum(1 for w in words if w in cls.SECOND_PERSON)
        third = sum(1 for w in words if w in cls.THIRD_PERSON)

        total_pronouns = first_sing + first_plur + second + third
        personal_pronouns = first_sing + first_plur + second
        
        # Impersonal index: percentage of 3rd person / impersonal pronouns out of total
        impersonal_ratio = round((third / max(total_pronouns, 1)) * 100.0, 1) if total_pronouns > 0 else 50.0

        return {
            "first_person_singular_count": first_sing,
            "first_person_plural_count": first_plur,
            "second_person_count": second,
            "third_person_count": third,
            "total_pronouns": total_pronouns,
            "first_person_pct": round(((first_sing + first_plur) / n) * 100.0, 2),
            "second_person_pct": round((second / n) * 100.0, 2),
            "third_person_pct": round((third / n) * 100.0, 2),
            "impersonal_ratio_pct": impersonal_ratio,
            "perspective": (
                "First-Person Subjective" if personal_pronouns > third and personal_pronouns >= 3 else
                "Direct Conversational (Second-Person)" if second >= 3 and second >= personal_pronouns else
                "Impersonal / Third-Person Objective"
            )
        }

    @classmethod
    def _calc_paragraph_metrics(cls, paragraphs: List[str], sentences: List[str]) -> Dict[str, Any]:
        p_count = max(len(paragraphs), 1)
        s_count = max(len(sentences), 1)

        p_lengths = [len(re.findall(r"\b[\w'-]+\b", p)) for p in paragraphs]
        mean_p_len = sum(p_lengths) / p_count
        
        if p_count > 1:
            var_p = sum((l - mean_p_len) ** 2 for l in p_lengths) / p_count
            std_p = math.sqrt(var_p)
            cv_p = std_p / max(mean_p_len, 1)
            # High uniformity = low CV (machine-like)
            uniformity = max(0.0, min(100.0, (1.0 - min(1.0, cv_p)) * 100.0))
        else:
            uniformity = 50.0
            std_p = 0.0

        return {
            "paragraph_count": p_count,
            "average_sentences_per_paragraph": round(s_count / p_count, 2),
            "average_words_per_paragraph": round(mean_p_len, 1),
            "paragraph_length_std_dev": round(std_p, 2),
            "uniformity_score": round(uniformity, 1)
        }

    @classmethod
    def _empty_result(cls) -> Dict[str, Any]:
        return {
            "average_sentence_length": 0.0,
            "sentence_complexity": {"average_clauses_per_sentence": 0.0, "subordinate_conjunctions_count": 0, "subordinate_clause_density": 0.0, "coordinate_conjunctions_count": 0, "complexity_level": "Simple"},
            "voice_distribution": {"active_sentences_count": 0, "passive_sentences_count": 0, "active_percentage": 100.0, "passive_percentage": 0.0, "dominant_voice": "Active"},
            "lexical_distribution": {"function_words_count": 0, "content_words_count": 0, "function_word_ratio": 0.0, "content_word_ratio": 0.0},
            "discourse_transitions": {"total_transitions": 0, "transition_density_per_100_words": 0.0, "markers_detected": []},
            "pronoun_usage": {"first_person_singular_count": 0, "first_person_plural_count": 0, "second_person_count": 0, "third_person_count": 0, "total_pronouns": 0, "first_person_pct": 0.0, "second_person_pct": 0.0, "third_person_pct": 0.0, "impersonal_ratio_pct": 50.0, "perspective": "Impersonal / Third-Person Objective"},
            "paragraph_structure": {"paragraph_count": 1, "average_sentences_per_paragraph": 0.0, "average_words_per_paragraph": 0.0, "paragraph_length_std_dev": 0.0, "uniformity_score": 50.0},
            "syntactic_formality_score": 0.0
        }
