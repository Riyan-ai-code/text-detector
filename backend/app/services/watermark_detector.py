import re
import math
import hashlib
from typing import Dict, Any, List


class WatermarkDetector:
    """
    Statistical AI Watermark Analysis Engine (Experimental):
    Implements statistical token green-list / red-list partitioning analysis
    (based on the Kirchenbauer et al. watermarking framework).
    Evaluates whether token transition hash residues exhibit non-random partitioning.
    """

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return cls._empty_result()

        words = re.findall(r"\b[\w'-]+\b", text.lower())
        n = len(words)

        if n < 30:
            return {
                "status": "Insufficient text for statistical watermarking analysis (min 30 words required)",
                "watermark_detected": False,
                "z_score": 0.0,
                "green_list_ratio": 0.50,
                "note": "Absence of a watermark does not establish human authorship.",
                "disclaimer": "Do not claim to detect proprietary or unknown watermarks without cryptographic verification."
            }

        # Pseudorandom hash partitioning simulation
        # For each token transition (w_{i-1}, w_i), hash(w_{i-1}) determines if w_i is in the green list
        green_hits = 0
        total_transitions = n - 1

        for i in range(total_transitions):
            prev_token = words[i]
            curr_token = words[i + 1]
            seed = hashlib.sha256(prev_token.encode("utf-8")).hexdigest()
            # 50% split threshold for pseudo green-list
            is_green_expected = (int(seed[:4], 16) % 2) == 0
            curr_hash = (int(hashlib.sha256(curr_token.encode("utf-8")).hexdigest()[:4], 16) % 2) == 0
            if is_green_expected == curr_hash:
                green_hits += 1

        observed_ratio = green_hits / max(total_transitions, 1)
        expected_ratio = 0.50
        variance = (expected_ratio * (1.0 - expected_ratio)) / total_transitions
        z_score = (observed_ratio - expected_ratio) / math.sqrt(variance) if variance > 0 else 0.0

        # Z-score >= 3.0 indicates statistically significant deviation from random null hypothesis (p < 0.001)
        is_watermark_present = z_score >= 3.20

        return {
            "status": "Statistical AI watermark pattern detected" if is_watermark_present else "No reliable watermark detected",
            "watermark_detected": is_watermark_present,
            "z_score": round(z_score, 2),
            "green_list_ratio": round(observed_ratio * 100, 1),
            "tokens_evaluated": total_transitions,
            "note": "Absence of a watermark does not establish human authorship.",
            "disclaimer": "Commercial LLM providers utilize proprietary or unreleased watermarking schemes. Statistical absence of a watermark pattern is not proof of human authorship."
        }

    @classmethod
    def _empty_result(cls) -> Dict[str, Any]:
        return {
            "status": "No reliable watermark detected",
            "watermark_detected": False,
            "z_score": 0.0,
            "green_list_ratio": 50.0,
            "note": "Absence of a watermark does not establish human authorship.",
            "disclaimer": "Do not claim to detect proprietary or unknown watermarks without evidence."
        }
