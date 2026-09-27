import pytest
from backend.app.services.authorship_segmenter import AuthorshipSegmenter
from backend.app.services.baseline_profiler import BaselineProfiler
from backend.app.services.watermark_detector import WatermarkDetector
from backend.app.services.paraphrase_detector import ParaphraseDetector
from backend.app.services.comparison_service import ComparisonService


DOC_HUMAN = (
    "I spent most of last weekend rummaging through my grandfather's attic, searching for an old wooden toolbox he used to carry everywhere. "
    "The air up there smelled like cedar and aged paper, and beneath a stack of dusty canvas tarps, I finally found it! "
    "Opening the rusted brass latch brought back a flood of memories—summer afternoons building lopsided birdhouses on the back porch."
)

DOC_AI = (
    "Artificial intelligence has revolutionized modern industries by augmenting human capabilities and automating repetitive tasks. "
    "Through advanced neural architectures and extensive pretraining on web-scale datasets, large language models exhibit remarkable proficiency "
    "across diverse domains including natural language understanding, creative synthesis, and semantic code generation. "
    "Furthermore, the integration of deep learning paradigms fosters unprecedented opportunities for accelerated scientific discovery."
)

MIXED_DOC = f"{DOC_HUMAN}\n\n{DOC_AI}\n\n{DOC_HUMAN}"


def test_authorship_segmenter_mixed():
    res = AuthorshipSegmenter.segment(MIXED_DOC)
    assert res["total_blocks"] >= 2
    assert "blocks" in res
    assert "distribution" in res
    assert res["is_mixed_authorship"] is True
    assert res["transitions_count"] >= 1
    assert any(t["from_block"] == 1 for t in res["transitions"])


def test_baseline_profiler_and_comparison():
    samples = [
        DOC_HUMAN,
        "Last Tuesday during our evening team walk, Sarah brought up how remote work altered our perceptions of time. We stopped for ice cream near the pier and debated whether scheduled unplugging works.",
        "When I started learning pottery two winters ago, my first dozen coffee mugs looked more like prehistoric clay relics than functional drinkware. The centering step is where everyone gets humbled."
    ]
    baseline = BaselineProfiler.create_baseline(samples, "Test Profile")
    assert baseline["sample_count"] == 3
    assert "metrics" in baseline
    assert baseline["metrics"]["avg_sentence_length"] > 0

    # Compare human text to baseline
    human_cmp = BaselineProfiler.compare_to_baseline(DOC_HUMAN, baseline)
    assert human_cmp["has_baseline"] is True
    assert human_cmp["style_similarity_pct"] >= 50.0

    # Compare AI text to human baseline
    ai_cmp = BaselineProfiler.compare_to_baseline(DOC_AI, baseline)
    assert ai_cmp["has_baseline"] is True
    assert ai_cmp["style_deviation_pct"] > 0
    assert len(ai_cmp["shift_explanations"]) > 0


def test_watermark_detector():
    res = WatermarkDetector.analyze(DOC_AI)
    assert "status" in res
    assert "watermark_detected" in res
    assert "z_score" in res
    assert "note" in res
    assert "Absence of a watermark does not establish human authorship" in res["note"]


def test_paraphrase_detector():
    res = ParaphraseDetector.detect(DOC_AI)
    assert "is_paraphrased_detected" in res
    assert "paraphrase_risk_score" in res
    assert "explanation" in res
    assert "disclaimer" in res


def test_comparison_service():
    res = ComparisonService.compare(DOC_HUMAN, DOC_AI)
    assert "document_a" in res
    assert "document_b" in res
    assert "divergence_score" in res
    assert res["document_a"]["word_count"] > 0
    assert res["document_b"]["word_count"] > 0
    assert len(res["divergence_insights"]) > 0
