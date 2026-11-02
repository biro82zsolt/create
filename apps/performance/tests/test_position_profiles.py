"""Unit tests for position_profiles.py; run with pytest -q."""

from position_profiles import (
    POSITION_LABELS, POSITION_TRAIT_WEIGHTS, score_position_fit, rank_positions,
)


def test_profile_uses_existing_app_codes():
    weights = POSITION_TRAIT_WEIGHTS["attacking_midfielder_playmaker"]
    assert weights["vision"] > 0  # Játékértés maps to existing vision code.
    assert "one_v_one_dominance" in POSITION_TRAIT_WEIGHTS["winger_classic"]
    assert "hard_to_beat" in POSITION_TRAIT_WEIGHTS["center_back_dominant"]


def test_weighted_score_excludes_missing_values_not_as_zero():
    weights = POSITION_TRAIT_WEIGHTS["attacking_midfielder_playmaker"]
    values = {"vision": 10, "decision_making": 8}
    result = score_position_fit(values, "attacking_midfielder_playmaker")
    assert result["categories"]["tactical"]["score"] == 9.0
    assert result["categories"]["tactical"]["coverage"] < 100


def test_uniform_scores_produce_same_score_when_profile_exists():
    values = {code: 7 for profile in POSITION_TRAIT_WEIGHTS.values() for code in profile}
    result = score_position_fit(values, "center_back_dominant")
    assert result["overall_score"] == 7.0


def test_physical_values_must_be_normalized_scores():
    result = score_position_fit(
        {code: 6 for code in POSITION_TRAIT_WEIGHTS["full_back_offensive"]},
        "full_back_offensive",
        {"height_cm": 7, "sprint_5m_seconds": 8},
    )
    assert result["categories"]["physical"]["score"] is not None
    assert result["categories"]["physical"]["coverage"] < 100


def test_goalkeeper_has_no_overall_score_until_trait_profile_exists():
    result = score_position_fit({}, "goalkeeper", {"height_cm": 9, "sprint_5m_seconds": 7})
    assert result["overall_score"] is None
    assert result["game_profile_defined"] is False


def test_unknown_position_fails_clearly():
    try:
        score_position_fit({}, "not_a_position")
    except ValueError as exc:
        assert "Unknown position profile" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_rank_positions_puts_unscored_profiles_last():
    values = {code: 6 for profile in POSITION_TRAIT_WEIGHTS.values() for code in profile}
    result = rank_positions(values, {"height_cm": 7, "sprint_5m_seconds": 6})
    assert result[-1]["position"] == "goalkeeper"
