import re
from collections import Counter
from typing import Dict, Any, List


class FingerprintAnalyzer:
    """
    Forensic AI Fingerprint & Model Family Engine:
    Detects formulaic LLM clichés, semantic uniformity, redundant syntactic openings,
    and calculates model-family pattern hypotheses (GPT-like, Claude-like, Gemini-like, Other).
    """

    LLM_CLICHES = [
        # Cognitive & Exploration Clichés
        "delve into", "delves into", "delving into", "shed light on", "sheds light on",
        "navigate the complexities", "navigating the complexities", "realm of", "realms of",
        "tapestry", "rich tapestry", "intricate tapestry", "testament to", "stands as a testament",
        "beacon of", "beacon of hope", "game-changer", "game changer", "vital role",
        "plays a vital role", "pivotal role", "plays a pivotal role", "crucial role",
        "in an era where", "in today's fast-paced", "in an increasingly automated",
        "in today's digital landscape", "rapidly evolving landscape", "evolving landscape",
        "fosters unprecedented", "unprecedented opportunities", "harness the power of",
        "harnessing the power", "multifaceted", "multifaceted nature", "double-edged sword",
        "serves as a reminder", "serves as a testament", "it is worth noting", "it's worth noting",
        "notably,", "importantly,", "consequently,", "furthermore,", "moreover,",
        "in conclusion,", "to conclude,", "in summary,", "all in all,", "at the end of the day",
        "underscores the importance", "highlights the need", "key takeaway", "key takeaways",
        "at its core", "deep dive", "transformative potential", "paradigm shift",
        "catalyst for change", "seamless integration", "holistic approach", "robust framework",
        "paving the way", "paves the way", "boundless possibilities", "indelible mark",
        "ever-evolving", "ever evolving", "cornerstone of", "bedrock of", "linchpin of",
        "symbiotic relationship", "crossroads of", "at the intersection of", "unravel the mystery",
        "dynamic interplay", "myriad of", "plethora of", "burgeoning field", "promising avenue"
    ]

    # Model Family Archetype Signatures
    GPT_SIGNATURE_PATTERNS = [
        r"\btestament to\b", r"\bdelve into\b", r"\btapestry\b", r"\bmultifaceted\b",
        r"\bfurthermore\b", r"\bmoreover\b", r"\bin summary\b", r"\bit is important to note\b",
        r"\brapidly evolving landscape\b", r"\bharness the power\b", r"\bpivotal role\b"
    ]

    CLAUDE_SIGNATURE_PATTERNS = [
        r"\bit is worth considering\b", r"\bwhile it is true that\b", r"\bfrom this perspective\b",
        r"\bcrucially\b", r"\bnotably\b", r"\bto be precise\b", r"\bnuanced understanding\b",
        r"\bin practical terms\b", r"\bcareful balance\b", r"\btrade-offs between\b"
    ]

    GEMINI_SIGNATURE_PATTERNS = [
        r"\bkey takeaways?\b", r"\bhere is a breakdown\b", r"\badditionally\b",
        r"\bsignificantly\b", r"\bin essence\b", r"\blooking ahead\b",
        r"\bcore advantages?\b", r"\bpractical application\b", r"\bsummary overview\b"
    ]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return cls._empty_result()

        raw_text = text.strip()
        lower_text = raw_text.lower()
        words = re.findall(r"\b[\w'-]+\b", raw_text)
        word_count = max(len(words), 1)

        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw_text) if s.strip()]
        if not raw_sentences:
            raw_sentences = [raw_text]

        # 1. Cliché Scan
        cliches_found = []
        for cliche in cls.LLM_CLICHES:
            count = len(re.findall(rf"\b{re.escape(cliche)}\b", lower_text))
            if count > 0:
                cliches_found.append({"cliche": cliche, "occurrences": count})

        total_cliches = sum(c["occurrences"] for c in cliches_found)
        cliche_density = round((total_cliches / word_count) * 100.0, 2)

        # 2. Syntactic Sentence Openings (Uniformity)
        opening_analysis = cls._analyze_sentence_openings(raw_sentences)

        # 3. Semantic Redundancy
        redundancy = cls._detect_semantic_redundancy(raw_sentences)

        # 4. Model-Family Classification Hypothesis
        family_hypothesis = cls._classify_model_family(lower_text, cliches_found, opening_analysis, word_count)

        # Composite Fingerprint Score (0-100)
        fingerprint_score = min(100.0, max(0.0, (
            (min(5.0, total_cliches) * 12.0) +
            (opening_analysis["monotony_score"] * 0.3) +
            (redundancy["redundancy_score"] * 0.3)
        )))

        return {
            "fingerprint_score": round(fingerprint_score, 1),
            "cliche_analysis": {
                "total_cliches_detected": total_cliches,
                "cliche_density_pct": cliche_density,
                "detected_phrases": cliches_found
            },
            "sentence_openings": opening_analysis,
            "semantic_redundancy": redundancy,
            "model_family_hypothesis": family_hypothesis
        }

    @classmethod
    def _analyze_sentence_openings(cls, sentences: List[str]) -> Dict[str, Any]:
        """Detects whether sentences start with repetitive syntactic constructs (e.g. Participles, Transitions)."""
        openings = []
        opening_types = Counter()

        for s in sentences:
            tokens = s.strip().split()
            if not tokens:
                continue
            first_word = tokens[0].lower().strip(",.!?;:")
            two_words = f"{tokens[0].lower()} {tokens[1].lower()}" if len(tokens) > 1 else first_word
            
            openings.append(first_word)
            
            # Categorize opening archetype
            if first_word.endswith("ing"):
                opening_types["participle_clause"] += 1
            elif first_word in {"furthermore", "moreover", "additionally", "consequently", "however", "therefore", "in"}:
                opening_types["formal_transition"] += 1
            elif first_word in {"the", "a", "an", "this", "these"}:
                opening_types["determiner_noun"] += 1
            elif first_word in {"i", "we", "you", "he", "she", "they", "it"}:
                opening_types["pronoun_subject"] += 1
            else:
                opening_types["other"] += 1

        n_sents = max(len(sentences), 1)
        # Monotony score: high when 1 opening type exceeds 60% of all sentences
        most_common_type, count = opening_types.most_common(1)[0] if opening_types else ("none", 0)
        dominant_ratio = count / n_sents
        monotony = round(min(100.0, max(0.0, (dominant_ratio - 0.35) * 150.0)), 1) if dominant_ratio > 0.35 else 10.0

        return {
            "monotony_score": monotony,
            "dominant_opening_type": most_common_type,
            "opening_type_distribution": dict(opening_types),
            "repetitive_openings_detected": dominant_ratio >= 0.5 and n_sents >= 4
        }

    @classmethod
    def _detect_semantic_redundancy(cls, sentences: List[str]) -> Dict[str, Any]:
        """Estimates inter-sentence semantic overlap and conceptual repetition."""
        if len(sentences) < 2:
            return {"redundancy_score": 20.0, "is_redundant": False, "high_overlap_pairs": []}

        overlap_pairs = []
        scores = []

        for i in range(len(sentences) - 1):
            w1 = set(re.findall(r"\b[a-z]{4,}\b", sentences[i].lower()))
            w2 = set(re.findall(r"\b[a-z]{4,}\b", sentences[i + 1].lower()))
            if not w1 or not w2:
                continue
            
            jaccard = len(w1 & w2) / len(w1 | w2)
            scores.append(jaccard)
            if jaccard >= 0.40:
                overlap_pairs.append({
                    "sentence_a_index": i + 1,
                    "sentence_b_index": i + 2,
                    "shared_content_words": list(w1 & w2)[:6],
                    "overlap_ratio": round(jaccard, 2)
                })

        avg_overlap = (sum(scores) / len(scores)) if scores else 0.0
        redundancy_score = round(min(100.0, avg_overlap * 200.0), 1)

        return {
            "redundancy_score": redundancy_score,
            "is_redundant": redundancy_score >= 50.0,
            "high_overlap_pairs": overlap_pairs
        }

    @classmethod
    def _classify_model_family(cls, lower_text: str, cliches: List[Dict], openings: Dict, word_count: int) -> Dict[str, Any]:
        """
        Heuristic multi-signal model-family indicator.
        Rules:
        - Never presents model identification as certain.
        - Returns probabilities and supporting evidence.
        - Falls back to 'Other / Unknown' if evidence is insufficient or confidence < 60%.
        """
        gpt_hits = sum(len(re.findall(p, lower_text)) for p in cls.GPT_SIGNATURE_PATTERNS)
        claude_hits = sum(len(re.findall(p, lower_text)) for p in cls.CLAUDE_SIGNATURE_PATTERNS)
        gemini_hits = sum(len(re.findall(p, lower_text)) for p in cls.GEMINI_SIGNATURE_PATTERNS)

        scores = {
            "GPT-like": gpt_hits * 2.5 + (1.5 if any(c["cliche"] in {"testament to", "delve into", "tapestry"} for c in cliches) else 0.0),
            "Claude-like": claude_hits * 2.5,
            "Gemini-like": gemini_hits * 2.5
        }

        total_score = sum(scores.values())

        if total_score < 2.5 or word_count < 60:
            return {
                "category": "Other / Unknown",
                "confidence": "Low",
                "probability": 0.35,
                "explanation": "Insufficient or mixed model-family patterns. Detection does not warrant a model-family attribution.",
                "disclaimer": "Model family identification is experimental and heuristic. It must never be taken as definitive evidence."
            }

        sorted_families = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_family, top_score = sorted_families[0]
        prob = round(min(0.85, max(0.40, top_score / (total_score + 1.0))), 2)

        conf_level = "Medium" if prob >= 0.65 else "Low"

        reasons = []
        if top_family == "GPT-like":
            reasons.append("High concentration of characteristic transition idioms, formulaic conclusion markers, and balanced clause density.")
        elif top_family == "Claude-like":
            reasons.append("Prevalence of conversational hedging, nuanced trade-off phrases, and deliberate structural qualification.")
        elif top_family == "Gemini-like":
            reasons.append("Direct explanatory formatting, section summary connectives, and concise synthesis cadence.")

        return {
            "category": top_family,
            "confidence": conf_level,
            "probability": prob,
            "explanation": " ".join(reasons),
            "scores_breakdown": {k: round(v, 1) for k, v in scores.items()},
            "disclaimer": "Model family categorization is an experimental statistical heuristic. Machine-generated text varies across fine-tunings, temperatures, and prompts."
        }

    @classmethod
    def _empty_result(cls) -> Dict[str, Any]:
        return {
            "fingerprint_score": 0.0,
            "cliche_analysis": {"total_cliches_detected": 0, "cliche_density_pct": 0.0, "detected_phrases": []},
            "sentence_openings": {"monotony_score": 0.0, "dominant_opening_type": "none", "opening_type_distribution": {}, "repetitive_openings_detected": False},
            "semantic_redundancy": {"redundancy_score": 0.0, "is_redundant": False, "high_overlap_pairs": []},
            "model_family_hypothesis": {"category": "Other / Unknown", "confidence": "Low", "probability": 0.0, "explanation": "No text analyzed.", "disclaimer": "Experimental heuristic only."}
        }
