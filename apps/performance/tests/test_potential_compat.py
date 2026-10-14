"""Smoke tests for Performance/Potential scoring compatibility."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scoring import ALL_PERFORMANCE_QUESTIONS, POTENTIAL_QUESTIONS, calculate_scores


def test_new_attribute_level_ratings():
    ratings = {question["code"]: 6 for question in ALL_PERFORMANCE_QUESTIONS}
    ratings.update({question["code"]: 8 for question in POTENTIAL_QUESTIONS})
    result = calculate_scores(ratings)
    assert result["performance"] == 6
    assert result["potential"] == 8
    assert result["potential_source"] == "attribute"


def test_legacy_category_level_ratings():
    ratings = {question["code"]: 6 for question in ALL_PERFORMANCE_QUESTIONS}
    ratings.update({
        "tactical_potential": 7,
        "technical_potential": 8,
        "behavioural_potential": 9,
    })
    result = calculate_scores(ratings)
    assert result["performance"] == 6
    assert result["potential"] == 8
    assert result["potential_source"] == "legacy_category"
