import re
import html
from typing import Dict, Any, List, Tuple


class TextDataNoiseCleaner:
    """
    Multi-stage Text Data Noise Removal & Normalization Engine.
    Filters:
    - HTML and XML tag artifacts (<p>, <script>, <div>, etc.)
    - HTML entity encodings (&nbsp;, &amp;, &quot;, &#39;)
    - Zero-width spaces and invisible adversarial watermarks (\u200b, \u200c, \u200d, \ufeff, \u2060)
    - LLM conversational boilerplate ("As an AI language model...", "Sure! Here is an essay:...")
    - Unicode mojibake and encoding corruption
    - Runaway whitespace, tabs, and duplicate newlines
    """

    # Zero-width / invisible unicode characters
    ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u2060", "\u200e", "\u200f", "\u00ad"]

    # Common LLM prompt/response boilerplate prefixes
    LLM_BOILERPLATE_PATTERNS = [
        r"^(?:as an ai language model|as an ai|as a large language model)[,\.\s]+",
        r"^(?:sure(?: thing)?|certainly|absolutely)[!,\.\s]+",
        r"^(?:here(?:'s| is) (?:an?|the) (?:comprehensive|detailed|brief)?\s*(?:essay|analysis|overview|article|response|paragraph|text|summary)?(?: (?:about|on|regarding)[^:\.\n]+)?[:\.\n\s]+)",
        r"^(?:in response to your request|i hope this helps)[!,\.\s]+",
    ]

    # Broken mojibake mapping
    MOJIBAKE_MAP = {
        "â€œ": '"',
        "â€\x9d": '"',
        "â€™": "'",
        "â€˜": "'",
        "â€”": "—",
        "â€“": "–",
        "Ã©": "é",
        "Ã¨": "è",
        "Ã ": "à",
        "Ã¢": "â",
        "Ã®": "î",
        "Ã§": "ç",
        "Â ": " ",
    }

    @classmethod
    def clean(cls, text: str) -> Dict[str, Any]:
        """
        Executes full multi-stage sanitization on text.
        Returns cleaned text along with a detailed breakdown of noise removed.
        """
        if not text:
            return {
                "cleaned_text": "",
                "original_length": 0,
                "cleaned_length": 0,
                "chars_removed": 0,
                "noise_detected": {
                    "html_tags_count": 0,
                    "zero_width_chars_count": 0,
                    "boilerplate_removed": False,
                    "mojibake_repaired_count": 0,
                    "excess_whitespace_collapsed": False,
                    "removed_snippets": []
                },
                "cleanliness_score": 100.0,
                "noise_ratio_percent": 0.0
            }

        original_len = len(text)
        current = text
        audit: Dict[str, Any] = {
            "html_tags_count": 0,
            "zero_width_chars_count": 0,
            "boilerplate_removed": False,
            "mojibake_repaired_count": 0,
            "excess_whitespace_collapsed": False,
            "removed_snippets": []
        }

        # 1. Zero-width invisible character stripping
        zw_count = 0
        for zw in cls.ZERO_WIDTH_CHARS:
            count = current.count(zw)
            if count > 0:
                zw_count += count
                current = current.replace(zw, "")
        audit["zero_width_chars_count"] = zw_count
        if zw_count > 0:
            audit["removed_snippets"].append(f"Neutralized {zw_count} invisible zero-width adversarial watermarks")

        # 2. Repair encoding mojibake
        moji_count = 0
        for bad, good in cls.MOJIBAKE_MAP.items():
            count = current.count(bad)
            if count > 0:
                moji_count += count
                current = current.replace(bad, good)
        audit["mojibake_repaired_count"] = moji_count

        # 3. Strip HTML / XML tags & unescape entities
        html_tags = re.findall(r"<[^>]+>", current)
        if html_tags:
            audit["html_tags_count"] = len(html_tags)
            audit["removed_snippets"].append(f"Stripped {len(html_tags)} raw HTML/XML tags")
            current = re.sub(r"<[^>]+>", " ", current)
        
        # Unescape HTML entities (&amp;, &nbsp;, etc.)
        current = html.unescape(current)

        # 4. Strip LLM conversational boilerplate headers (iterative prefix stripping)
        stripped_current = current.strip()
        matched_any = True
        while matched_any:
            matched_any = False
            for pattern in cls.LLM_BOILERPLATE_PATTERNS:
                match = re.match(pattern, stripped_current, flags=re.IGNORECASE)
                if match:
                    matched_text = match.group(0)
                    stripped_current = stripped_current[len(matched_text):].lstrip()
                    audit["boilerplate_removed"] = True
                    audit["removed_snippets"].append(f"Removed AI conversational preamble: '{matched_text.strip()}'")
                    matched_any = True
                    break
        current = stripped_current

        # 5. Normalize whitespace, tabs, and excess newlines
        prev_len = len(current)
        # Collapse 3+ newlines to 2
        current = re.sub(r"\n{3,}", "\n\n", current)
        # Replace non-breaking spaces and tabs with standard space
        current = current.replace("\u00a0", " ").replace("\t", " ")
        # Collapse multiple spaces to single
        current = re.sub(r"[ ]{2,}", " ", current)
        current = current.strip()

        if len(current) < prev_len:
            audit["excess_whitespace_collapsed"] = True

        cleaned_len = len(current)
        chars_removed = max(0, original_len - cleaned_len)
        noise_ratio = round((chars_removed / max(original_len, 1)) * 100, 2)

        # Output cleanliness score is 100% when all noise artifacts are removed
        remaining_noise = (1 if re.search(r"<[^>]+>", current) else 0) + sum(current.count(z) for z in cls.ZERO_WIDTH_CHARS)
        cleanliness_score = 100.0 if remaining_noise == 0 else max(0.0, round(100.0 - (remaining_noise * 10.0), 1))

        return {
            "cleaned_text": current,
            "original_length": original_len,
            "cleaned_length": cleaned_len,
            "chars_removed": chars_removed,
            "noise_detected": audit,
            "cleanliness_score": cleanliness_score,
            "noise_ratio_percent": noise_ratio
        }


data_cleaner = TextDataNoiseCleaner()
