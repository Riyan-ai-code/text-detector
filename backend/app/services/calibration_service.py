from typing import Dict, Any, List


class CalibrationService:
    """
    Anti-False-Positive & Confidence Calibration Engine:
    Applies statistical guardrails, detects sample size deficiencies (<100 words),
    evaluates domain biases (academic, legal, translated), and calibrates
    uncertainty ratings with explainable warning disclaimers.
    """

    CRITICAL_SHORT_THRESHOLD = 50
    RECOMMENDED_MIN_THRESHOLD = 100
    OPTIMAL_MIN_THRESHOLD = 250

    ACADEMIC_SIGNALS = [
        "empirical", "methodology", "statistically", "hypothesis", "significance",
        "parameters", "generalization", "benchmark", "corpus", "anisotropic",
        "curvature", "eigenvalues", "hessian", "stochastic"
    ]

    LEGAL_SIGNALS = [
        "hereto", "thereunder", "indemnify", "pursuant to", "notwithstanding",
        "force majeure", "jurisdiction", "governing law", "clause", "statute"
    ]

    @classmethod
    def calibrate(
        cls,
        text: str,
        word_count: int,
        raw_probability: float,
        model_agreement_ratio: float,
        statistical_signals: Dict[str, Any],
        stylometric_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        warnings = []
        domain_caveats = []
        confidence_level = "HIGH"
        reliability_score = 100.0  # 0 to 100 scale

        lower_text = text.lower()

        # 1. Sample Size Assessment
        if word_count < cls.CRITICAL_SHORT_THRESHOLD:
            confidence_level = "LOW"
            reliability_score -= 50.0
            warnings.append({
                "code": "CRITICALLY_SHORT_SAMPLE",
                "severity": "HIGH",
                "message": f"Only {word_count} words analyzed. Statistical variance is high; detection reliability is severely constrained for passages under 50 words."
            })
        elif word_count < cls.RECOMMENDED_MIN_THRESHOLD:
            confidence_level = "MEDIUM" if confidence_level == "HIGH" else confidence_level
            reliability_score -= 30.0
            warnings.append({
                "code": "SHORT_TEXT_SAMPLE",
                "severity": "MEDIUM",
                "message": f"Only {word_count} words analyzed. Statistical variance is elevated. For higher forensic reliability, submit passages of 150–250+ words."
            })
        elif word_count < cls.OPTIMAL_MIN_THRESHOLD:
            reliability_score -= 10.0

        # 2. Domain Bias Checks (Academic / Scholarly)
        academic_hits = sum(1 for term in cls.ACADEMIC_SIGNALS if term in lower_text)
        if academic_hits >= 3:
            domain_caveats.append({
                "domain": "Academic / Scholarly Prose",
                "risk": "Elevated False-Positive Risk",
                "explanation": "Formal scientific papers and peer-reviewed abstracts naturally exhibit low lexical burstiness and high passive voice, which can mimic AI patterns."
            })
            if confidence_level == "HIGH":
                confidence_level = "MEDIUM"
            reliability_score -= 15.0

        # Legal / Regulatory Prose
        legal_hits = sum(1 for term in cls.LEGAL_SIGNALS if term in lower_text)
        if legal_hits >= 2:
            domain_caveats.append({
                "domain": "Legal / Contractual Text",
                "risk": "Elevated False-Positive Risk",
                "explanation": "Legal boilerplate relies on standardized phrases and structured clauses that naturally produce high predictability scores."
            })
            if confidence_level == "HIGH":
                confidence_level = "MEDIUM"
            reliability_score -= 15.0

        # 3. Model Disagreement Penalty
        if model_agreement_ratio < 0.67:
            if confidence_level == "HIGH":
                confidence_level = "MEDIUM"
            reliability_score -= 20.0
            warnings.append({
                "code": "MODEL_DISAGREEMENT",
                "severity": "MEDIUM",
                "message": "Underlying neural and statistical classifiers diverge on this text. Signals are heterogeneous across feature dimensions."
            })

        # 4. Borderline Probability Range (40% - 65%)
        if 0.40 <= raw_probability <= 0.65:
            confidence_level = "LOW" if confidence_level == "MEDIUM" else confidence_level
            reliability_score -= 20.0
            warnings.append({
                "code": "BORDERLINE_PROBABILITY",
                "severity": "LOW",
                "message": "Composite AI-like probability falls within the uncertain/borderline band (40%–65%). The text contains a blend of human and synthetic stylistic markers."
            })

        # 5. Core Anti-False-Positive Product Rule Disclaimers
        reliability_score = max(10.0, min(100.0, reliability_score))

        core_assessment_text = (
            "The document contains several statistical and stylistic patterns commonly associated with AI-generated text. "
            "These signals are probabilistic indicators and NOT proof of AI authorship."
            if raw_probability >= 0.55 else
            "The document predominantly exhibits stylistic variance, burstiness, and personal lexical markers consistent with human authorship."
            if raw_probability <= 0.40 else
            "The document exhibits mixed authorship indicators with conflicting statistical signals. A definitive attribution cannot be established."
        )

        return {
            "calibrated_confidence": confidence_level,
            "reliability_index": round(reliability_score, 1),
            "warnings": warnings,
            "domain_caveats": domain_caveats,
            "has_warnings": len(warnings) > 0,
            "has_domain_caveats": len(domain_caveats) > 0,
            "anti_false_positive_disclaimer": (
                "TruthLens AI provides probabilistic pattern analysis based on empirical language modeling. "
                "No automated detector is 100% accurate. Results must be treated as supporting evidence within a broader editorial review, never as conclusive proof."
            ),
            "executive_assessment": core_assessment_text
        }
