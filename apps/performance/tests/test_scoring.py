import pytest

from .scoring import (
    ALL_QUESTIONS,
    POTENTIAL_QUESTIONS,
    validate_assessment,
    calculate_scores,
)


def baseline(value=6, potential_value=8):
    scores = {q["code"]: value for q in ALL_QUESTIONS}
    for question in POTENTIAL_QUESTIONS:
        scores[question["code"]] = potential_value
    return scores


def test_new_model_requires_52_attribute_ratings():
    scores = baseline()
    assert len(ALL_QUESTIONS) == 52
    assert validate_assessment(scores) is True
    del scores["potential_finding_space"]
    with pytest.raises(ValueError, match="Hiányzó értékelések"):
        validate_assessment(scores)


def test_performance_and_potential_are_scored_separately():
    result = calculate_scores(baseline(value=6, potential_value=8))
    assert result["performance"] == 6
    assert result["potential"] == 8
    assert result["tactical_potential"] == 8
    assert result["technical_potential"] == 8
    assert result["behavioural_potential"] == 8


def test_partial_potential_is_rejected():
    scores = baseline()
    scores.pop("potential_vision")
    with pytest.raises(ValueError):
        calculate_scores(scores)
