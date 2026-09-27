import re
import unicodedata
from typing import Dict, Any, List, Tuple

# Mapping of common homoglyphs (Cyrillic/Greek lookalikes) to standard Latin ASCII characters
HOMOGLYPH_MAP = {
    # Cyrillic lowercase
    "\u0430": "a",  # а
    "\u0435": "e",  # е
    "\u043e": "o",  # о
    "\u0440": "p",  # р
    "\u0441": "c",  # с
    "\u0443": "y",  # у
    "\u0445": "x",  # х
    "\u0456": "i",  # і
    "\u0458": "j",  # ј
    "\u0455": "s",  # ѕ
    # Cyrillic uppercase
    "\u0410": "A",  # А
    "\u0412": "B",  # В
    "\u0415": "E",  # Е
    "\u041a": "K",  # К
    "\u041c": "M",  # М
    "\u041d": "H",  # Н
    "\u041e": "O",  # О
    "\u0420": "P",  # Р
    "\u0421": "C",  # С
    "\u0422": "T",  # Т
    "\u0425": "X",  # Х
    # Greek lowercase
    "\u03bf": "o",  # ο
    "\u03bd": "v",  # ν
    "\u03ba": "k",  # κ
    "\u03c1": "p",  # ρ
}

# Invisible and zero-width code points
ZERO_WIDTH_CHARS = {
    "\u200b": "Zero-Width Space (U+200B)",
    "\u200c": "Zero-Width Non-Joiner (U+200C)",
    "\u200d": "Zero-Width Joiner (U+200D)",
    "\ufeff": "Zero-Width No-Break Space (U+FEFF)",
    "\u2060": "Word Joiner (U+2060)",
    "\u00ad": "Soft Hyphen (U+00AD)",
    "\u200e": "Left-to-Right Mark (U+200E)",
    "\u200f": "Right-to-Left Mark (U+200F)",
}

# Known formulaic AI cliches and buzzword phrases heavily overrepresented in LLM generated text
AI_CLICHE_PATTERNS = [
    "delve into", "delves into", "delving into",
    "testament to", "a testament to",
    "it is crucial to note", "it is important to note",
    "crucial role", "pivotal role",
    "in conclusion", "to summarize",
    "tapestry of", "rich tapestry",
    "beacon of", "beacon of hope",
    "multifaceted", "ever-evolving", "rapidly evolving",
    "fosters unprecedented", "unprecedented opportunities",
    "revolutionized modern", "revolutionizing the",
    "serves as a reminder", "serves as a testament",
    "at the forefront of", "paramount importance",
    "underscores the", "underscores the need",
    "in essence", "seamlessly integrates", "plays an indispensable role"
]


class EvasionService:
    """
    Detects and sanitizes adversarial evasion attempts designed to bypass
    AI text detectors, including hidden unicode characters, homoglyphs,
    and formulaic AI stylistic clichés.
    """

    @classmethod
    def scan_and_sanitize(cls, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "is_tampered": False,
                "evasion_score_pct": 0.0,
                "zero_width_count": 0,
                "homoglyphs_count": 0,
                "tampering_details": [],
                "sanitized_text": "",
                "ai_cliches_found": [],
                "cliche_count": 0
            }

        tampering_details: List[str] = []
        zero_width_count = 0
        zero_width_types = set()

        # 1. Scan for invisible / zero-width characters
        for char, name in ZERO_WIDTH_CHARS.items():
            count = text.count(char)
            if count > 0:
                zero_width_count += count
                zero_width_types.add(name)

        if zero_width_count > 0:
            tampering_details.append(
                f"Detected {zero_width_count} invisible zero-width character(s): {', '.join(sorted(zero_width_types))}"
            )

        # 2. Scan for homoglyphs (lookalike characters from other scripts)
        homoglyphs_count = 0
        detected_homoglyphs = {}
        sanitized_chars = []

        for char in text:
            # If zero-width character, strip it
            if char in ZERO_WIDTH_CHARS:
                continue
            # If homoglyph, replace with standard Latin character
            if char in HOMOGLYPH_MAP:
                homoglyphs_count += 1
                replacement = HOMOGLYPH_MAP[char]
                detected_homoglyphs[char] = replacement
                sanitized_chars.append(replacement)
            else:
                sanitized_chars.append(char)

        sanitized_text = "".join(sanitized_chars)

        if homoglyphs_count > 0:
            examples = [f"'{k}' -> '{v}'" for k, v in list(detected_homoglyphs.items())[:4]]
            tampering_details.append(
                f"Detected {homoglyphs_count} homoglyph character(s) (e.g., {', '.join(examples)})"
            )

        # 3. Scan for AI Clichés & Formulaic Transitions
        lower_sanitized = sanitized_text.lower()
        ai_cliches_found: List[Dict[str, Any]] = []

        for phrase in AI_CLICHE_PATTERNS:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            matches = list(re.finditer(pattern, lower_sanitized))
            if matches:
                ai_cliches_found.append({
                    "phrase": phrase,
                    "count": len(matches),
                    "positions": [m.start() for m in matches]
                })

        # 4. Calculate Evasion Score (0 - 100%)
        evasion_weight = (zero_width_count * 25.0) + (homoglyphs_count * 15.0)
        evasion_score = min(100.0, round(evasion_weight, 1))
        is_tampered = evasion_score > 0

        return {
            "is_tampered": is_tampered,
            "evasion_score_pct": evasion_score,
            "zero_width_count": zero_width_count,
            "homoglyphs_count": homoglyphs_count,
            "tampering_details": tampering_details,
            "sanitized_text": sanitized_text,
            "ai_cliches_found": ai_cliches_found,
            "cliche_count": sum(item["count"] for item in ai_cliches_found)
        }
