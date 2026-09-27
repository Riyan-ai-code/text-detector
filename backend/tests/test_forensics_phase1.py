import pytest
from backend.app.services.statistical_analyzer import StatisticalAnalyzer
from backend.app.services.stylometric_analyzer import StylometricAnalyzer
from backend.app.services.fingerprint_analyzer import FingerprintAnalyzer
from backend.app.services.calibration_service import CalibrationService
from backend.model_service import model_service


AI_SAMPLE = (
    "Artificial intelligence has revolutionized modern industries by augmenting human capabilities "
    "and automating repetitive tasks. Through advanced neural architectures and extensive pretraining on web-scale datasets, "
    "large language models exhibit remarkable proficiency across diverse domains including natural language understanding, "
    "creative synthesis, and semantic code generation. Furthermore, the integration of deep learning paradigms fosters "
    "unprecedented opportunities for accelerated scientific discovery. In essence, this technological revolution serves as "
    "a testament to human ingenuity and underscores the importance of ethical governance as we delve into an increasingly automated future."
)

HUMAN_SAMPLE = (
    "I spent most of last weekend rummaging through my grandfather's attic, searching for an old wooden toolbox he used to carry everywhere. "
    "The air up there smelled like cedar and aged paper, and beneath a stack of dusty canvas tarps, I finally found it! "
    "Opening the rusted brass latch brought back a flood of memories—summer afternoons building lopsided birdhouses on the back porch while listening "
    "to the hum of cicadas in the maple trees. Dad used to say quality tools outlive their owners, and he wasn't wrong. Can you imagine using a hammer for fifty years?"
)

SHORT_SAMPLE = "Only twenty words in this short test passage right here."


def test_statistical_analyzer():
    res = StatisticalAnalyzer.analyze(AI_SAMPLE)
    assert res["counts"]["word_count"] > 50
    assert "perplexity" in res
    assert "burstiness" in res
    assert "vocabulary_diversity" in res
    assert res["vocabulary_diversity"]["simpsons_diversity_index"] > 0
    assert res["vocabulary_diversity"]["shannon_entropy"] > 0
    assert "ngram_repetitions" in res
    assert "punctuation_distribution" in res
    assert res["punctuation_distribution"]["total_punctuation_marks"] > 0


def test_stylometric_analyzer():
    res = StylometricAnalyzer.analyze(AI_SAMPLE)
    assert res["average_sentence_length"] > 0
    assert "sentence_complexity" in res
    assert "voice_distribution" in res
    assert res["voice_distribution"]["active_percentage"] >= 0
    assert res["voice_distribution"]["passive_percentage"] >= 0
    assert "lexical_distribution" in res
    assert res["lexical_distribution"]["function_word_ratio"] > 0
    assert "pronoun_usage" in res
    assert "paragraph_structure" in res


def test_fingerprint_analyzer():
    res = FingerprintAnalyzer.analyze(AI_SAMPLE)
    assert res["cliche_analysis"]["total_cliches_detected"] >= 2
    detected = [c["cliche"] for c in res["cliche_analysis"]["detected_phrases"]]
    assert any(c in detected for c in ["delve into", "testament to", "furthermore"])
    assert "model_family_hypothesis" in res
    assert res["model_family_hypothesis"]["category"] in ["GPT-like", "Claude-like", "Gemini-like", "Other / Unknown"]
    assert "disclaimer" in res["model_family_hypothesis"]


def test_calibration_service_short_sample():
    stat = StatisticalAnalyzer.analyze(SHORT_SAMPLE)
    stylo = StylometricAnalyzer.analyze(SHORT_SAMPLE)
    calib = CalibrationService.calibrate(
        text=SHORT_SAMPLE,
        word_count=stat["counts"]["word_count"],
        raw_probability=0.85,
        model_agreement_ratio=1.0,
        statistical_signals=stat,
        stylometric_signals=stylo
    )
    assert calib["calibrated_confidence"] in ["LOW", "MEDIUM"]
    assert calib["has_warnings"] is True
    assert any(w["code"] == "CRITICALLY_SHORT_SAMPLE" for w in calib["warnings"])
    assert "anti_false_positive_disclaimer" in calib


def test_model_service_analyze_full_phase1_integration():
    res = model_service.analyze_full(AI_SAMPLE)
    assert "counts" in res
    assert "statistical_signals" in res
    assert "stylometric_signals" in res
    assert "fingerprint_signals" in res
    assert "calibration" in res
    assert res["counts"]["word_count"] > 50
    assert res["calibration"]["calibrated_confidence"] in ["HIGH", "MEDIUM", "LOW"]
