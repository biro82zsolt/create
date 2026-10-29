"""Position-specific fit scoring for the Performance app.

The 0-4 football-trait weights are transcribed from the approved workbook.
Physical weights are provisional staff hypotheses, not validated norms.
Physical inputs accepted by score_position_fit must already be normalized to
a 1-10 score (raw seconds/height/VO2max are deliberately not converted here).

This module is additive: it does not change the existing Performance/Potential
scoring engine.
"""

from __future__ import annotations

from math import isfinite
from typing import Any, Mapping

CATEGORY_WEIGHTS = {
    "tactical": 0.35,
    "technical": 0.30,
    "behaviour": 0.20,
    "physical": 0.15,
}

ATTRIBUTE_CATEGORIES = {
    "finding_space": "tactical",
    "vision": "tactical",
    "decision_making": "tactical",
    "support_play": "tactical",
    "reading_play": "tactical",
    "reaction_to_losing_ball": "tactical",
    "ball_control": "technical",
    "receiving_under_pressure": "technical",
    "twisting_turning": "technical",
    "one_v_one_dominance": "technical",
    "dribbling": "technical",
    "passing_range": "technical",
    "passing_quality": "technical",
    "attacking_heading": "technical",
    "crossing": "technical",
    "finishing": "technical",
    "hard_to_beat": "technical",
    "defensive_heading": "technical",
    "tackling": "technical",
    "interceptions": "technical",
    "competitive_edge": "behaviour",
    "bravery_on_ball": "behaviour",
    "bravery_without_ball": "behaviour",
    "control": "behaviour",
    "concentration": "behaviour",
    "communication": "behaviour",
}

PHYSICAL_METRICS = {
    "height_cm": "Testmagasság (cm)",
    "sprint_5m_seconds": "5 m sprint (másodperc)",
    "sprint_30m_seconds": "30 m sprint (másodperc)",
    "vo2max": "VO₂max",
}

POSITION_LABELS_HU = {
    "goalkeeper": "Kapus",
    "center_back_dominant": "Belső védő – domináns",
    "center_back_ballplaying": "Belső védő – labdakihozatalban erős",
    "full_back_offensive": "Szélső védő – támadó",
    "full_back_defensive": "Szélső védő – védekező",
    "defensive_midfielder_deep_playmaker": "Védekező középpályás – mélységi irányító",
    "defensive_midfielder_holding": "Védekező középpályás – labdaszerző/szűrő",
    "central_midfielder_box_to_box": "Középső középpályás – box-to-box",
    "attacking_midfielder_playmaker": "Támadó középpályás – irányító",
    "attacking_midfielder_shadow_striker": "Támadó középpályás – második csatár",
    "winger_classic": "Szélső – klasszikus szélső",
    "winger_wide_playmaker": "Szélső – szélső irányító",
    "striker_goalscorer": "Csatár – góllövő",
    "striker_target_player": "Csatár – target player",
}

POSITION_LABELS = {'goalkeeper': 'Goalkeeper',
 'center_back_dominant': 'Center Back Dominant',
 'center_back_ballplaying': 'Center Back Ballplaying',
 'full_back_offensive': 'Full Back Offensive',
 'full_back_defensive': 'Full Back Defensive',
 'defensive_midfielder_deep_playmaker': 'Defensive Midfielder Deep playmaker',
 'defensive_midfielder_holding': 'Defensive Midfielder Holding',
 'central_midfielder_box_to_box': 'Central Midfielder Box-to-box',
 'attacking_midfielder_playmaker': 'Attacking Midfielder Attacking playmaker',
 'attacking_midfielder_shadow_striker': 'Attacking Midfielder Shadow Striker',
 'winger_classic': 'Winger classic winger',
 'winger_wide_playmaker': 'Winger wide playmaker',
 'striker_goalscorer': 'Striker goalscorer',
 'striker_target_player': 'Striker target player'}

POSITION_TRAIT_WEIGHTS = {'goalkeeper': {},
 'center_back_dominant': {'finding_space': 1.5,
                          'vision': 1.25,
                          'decision_making': 1.25,
                          'support_play': 1.0,
                          'reading_play': 1.25,
                          'reaction_to_losing_ball': 1.0,
                          'ball_control': 1.0,
                          'receiving_under_pressure': 1.0,
                          'twisting_turning': 1.0,
                          'one_v_one_dominance': 1.0,
                          'dribbling': 1.0,
                          'passing_range': 1.5,
                          'passing_quality': 1.25,
                          'attacking_heading': 1.25,
                          'crossing': 1.0,
                          'finishing': 1.0,
                          'hard_to_beat': 2.0,
                          'defensive_heading': 2.0,
                          'tackling': 2.0,
                          'interceptions': 2.0,
                          'competitive_edge': 1.5,
                          'bravery_on_ball': 1.25,
                          'bravery_without_ball': 1.0,
                          'control': 1.25,
                          'concentration': 1.5,
                          'communication': 2.0},
 'center_back_ballplaying': {'finding_space': 1.0,
                             'vision': 1.5,
                             'decision_making': 1.5,
                             'support_play': 1.5,
                             'reading_play': 2.0,
                             'reaction_to_losing_ball': 1.0,
                             'ball_control': 2.0,
                             'receiving_under_pressure': 1.75,
                             'twisting_turning': 1.25,
                             'one_v_one_dominance': 1.0,
                             'dribbling': 1.25,
                             'passing_range': 2.0,
                             'passing_quality': 2.0,
                             'attacking_heading': 1.0,
                             'crossing': 1.0,
                             'finishing': 1.0,
                             'hard_to_beat': 1.25,
                             'defensive_heading': 1.25,
                             'tackling': 1.25,
                             'interceptions': 1.5,
                             'competitive_edge': 1.0,
                             'bravery_on_ball': 2.0,
                             'bravery_without_ball': 1.0,
                             'control': 1.25,
                             'concentration': 1.5,
                             'communication': 1.75,},

'full_back_offensive': {'finding_space': 1.25,
                         'vision': 1.0,
                         'decision_making': 1.0,
                         'support_play': 1.25,
                         'reading_play': 1.25,
                         'reaction_to_losing_ball': 1.5,
                         'ball_control': 1.0,
                         'receiving_under_pressure': 1.5,
                         'twisting_turning': 1.0,
                         'one_v_one_dominance': 2.0,
                         'dribbling': 2.0,
                         'passing_range': 1.25,
                         'passing_quality': 1.75,
                         'attacking_heading': 1.0,
                         'crossing': 2.0,
                         'finishing': 1.0,
                         'hard_to_beat': 1.5,
                         'defensive_heading': 1.25,
                         'tackling': 1.25,
                         'interceptions': 1.25,
                         'competitive_edge': 1.75,
                         'bravery_on_ball': 1.75,
                         'bravery_without_ball': 1.0,
                         'control': 1.0,
                         'concentration': 1.0,
                         'communication': 1.0},
 'full_back_defensive': {'finding_space': 1.0,
                         'vision': 1.0,
                         'decision_making': 1.0,
                         'support_play': 1.0,
                         'reading_play': 1.5,
                         'reaction_to_losing_ball': 1.75,
                         'ball_control': 1.0,
                         'receiving_under_pressure': 1.0,
                         'twisting_turning': 1.0,
                         'one_v_one_dominance': 1.25,
                         'dribbling': 1.25,
                         'passing_range': 1.0,
                         'passing_quality': 1.0,
                         'attacking_heading': 1.0,
                         'crossing': 1.5,
                         'finishing': 1.0,
                         'hard_to_beat': 2.0,
                         'defensive_heading': 1.75,
                         'tackling': 2.0,
                         'interceptions': 2.0,
                         'competitive_edge': 1.75,
                         'bravery_on_ball': 1.0,
                         'bravery_without_ball': 1.5,
                         'control': 1.25,
                         'concentration': 1.0,
                         'communication': 1.0},
'defensive_midfielder_deep_playmaker': {'finding_space': 2.0,
                                         'vision': 2.0,
                                         'decision_making': 2.0,
                                         'support_play': 1.5,
                                         'reading_play': 1.75,
                                         'reaction_to_losing_ball': 1.0,
                                         'ball_control': 2.0,
                                         'receiving_under_pressure': 2.0,
                                         'twisting_turning': 2.0,
                                         'one_v_one_dominance': 1.0,
                                         'dribbling': 1.25,
                                         'passing_range': 2.0,
                                         'passing_quality': 2.0,
                                         'attacking_heading': 1.0,
                                         'crossing': 1.0,
                                         'finishing': 1.0,
                                         'hard_to_beat': 1.0,
                                         'defensive_heading': 1.0,
                                         'tackling': 1.5,
                                         'interceptions': 1.5,
                                         'competitive_edge': 1.0,
                                         'bravery_on_ball': 2.0,
                                         'bravery_without_ball': 1.0,
                                         'control': 1.25,
                                         'concentration': 2.0,
                                         'communication': 1.75},
 'defensive_midfielder_holding': {'finding_space': 1.25,
                                  'vision': 1.25,
                                  'decision_making': 1.0,
                                  'support_play': 1.0,
                                  'reading_play': 1.75,
                                  'reaction_to_losing_ball': 1.75,
                                  'ball_control': 1.25,
                                  'receiving_under_pressure': 1.5,
                                  'twisting_turning': 1.5,
                                  'one_v_one_dominance': 1.0,
                                  'dribbling': 1.0,
                                  'passing_range': 1.25,
                                  'passing_quality': 1.25,
                                  'attacking_heading': 1.0,
                                  'crossing': 1.0,
                                  'finishing': 1.0,
                                  'hard_to_beat': 1.75,
                                  'defensive_heading': 1.75,
                                  'tackling': 2.0,
                                  'interceptions': 2.0,
                                  'competitive_edge': 2.0,
                                  'bravery_on_ball': 1.0,
                                  'bravery_without_ball': 2.0,
                                  'control': 1.5,
                                  'concentration': 1.25,
                                  'communication': 1.5},
 'central_midfielder_box_to_box': {'finding_space': 1.5,
                                   'vision': 1.25,
                                   'decision_making': 1.0,
                                   'support_play': 1.75,
                                   'reading_play': 1.5,
                                   'reaction_to_losing_ball': 2.0,
                                   'ball_control': 1.25,
                                   'receiving_under_pressure': 1.5,
                                   'twisting_turning': 1.75,
                                   'one_v_one_dominance': 1.5,
                                   'dribbling': 2.0,
                                   'passing_range': 1.5,
                                   'passing_quality': 1.75,
                                   'attacking_heading': 1.0,
                                   'crossing': 1.0,
                                   'finishing': 1.25,
                                   'hard_to_beat': 1.5,
                                   'defensive_heading': 1.0,
                                   'tackling': 1.75,
                                   'interceptions': 1.5,
                                   'competitive_edge': 2.0,
                                   'bravery_on_ball': 1.75,
                                   'bravery_without_ball': 1.5,
                                   'control': 1.0,
                                   'concentration': 1.25,
                                   'communication': 1.0},
'attacking_midfielder_playmaker': {'finding_space': 1.25,
                                   'vision': 2.0,
                                   'decision_making': 2.0,
                                   'support_play': 1.25,
                                   'reading_play': 1.0,
                                   'reaction_to_losing_ball': 1.0,
                                   'ball_control': 2.0,
                                   'receiving_under_pressure': 2.0,
                                   'twisting_turning': 2.0,
                                   'one_v_one_dominance': 1.0,
                                   'dribbling': 1.25,
                                   'passing_range': 1.75,
                                   'passing_quality': 2.0,
                                   'attacking_heading': 1.0,
                                   'crossing': 1.25,
                                   'finishing': 1.25,
                                   'hard_to_beat': 1.0,
                                   'defensive_heading': 1.0,
                                   'tackling': 1.0,
                                   'interceptions': 1.0,
                                   'competitive_edge': 1.25,
                                   'bravery_on_ball': 2.0,
                                   'bravery_without_ball': 1.0,
                                   'control': 1.0,
                                   'concentration': 1.25,
                                   'communication': 1.5},
'attacking_midfielder_shadow_striker': {'finding_space': 2.0,
                                        'vision': 1.25,
                                        'decision_making': 1.25,
                                        'support_play': 2.0,
                                        'reading_play': 1.0,
                                        'reaction_to_losing_ball': 1.25,
                                        'ball_control': 1.25,
                                        'receiving_under_pressure': 1.25,
                                        'twisting_turning': 1.5,
                                        'one_v_one_dominance': 2.0,
                                        'dribbling': 1.75,
                                        'passing_range': 1.0,
                                        'passing_quality': 1.25,
                                        'attacking_heading': 1.5,
                                        'crossing': 1.0,
                                        'finishing': 2.0,
                                        'hard_to_beat': 1.0,
                                        'defensive_heading': 1.0,
                                        'tackling': 1.0,
                                        'interceptions': 1.0,
                                        'competitive_edge': 1.75,
                                        'bravery_on_ball': 2.0,
                                        'bravery_without_ball': 1.5,
                                        'control': 1.0,
                                        'concentration': 1.0,
                                        'communication': 1.0},
'winger_classic': {'finding_space': 1.5,
                   'vision': 1.0,
                   'decision_making': 1.5,
                   'support_play': 1.25,
                   'reading_play': 1.0,
                   'reaction_to_losing_ball': 1.25,
                   'ball_control': 1.75,
                   'receiving_under_pressure': 1.5,
                   'twisting_turning': 1.75,
                   'one_v_one_dominance': 2.0,
                   'dribbling': 2.0,
                   'passing_range': 1.0,
                   'passing_quality': 1.5,
                   'attacking_heading': 1.25,
                   'crossing': 2.0,
                   'finishing': 1.75,
                   'hard_to_beat': 1.0,
                   'defensive_heading': 1.0,
                   'tackling': 1.0,
                   'interceptions': 1.0,
                   'competitive_edge': 1.5,
                   'bravery_on_ball': 2.0,
                   'bravery_without_ball': 1.75,
                   'control': 1.0,
                   'concentration': 1.0,
                   'communication': 1.0},

'winger_wide_playmaker': {'finding_space': 1.5,
                          'vision': 1.0,
                          'decision_making': 1.5,
                          'support_play': 1.25,
                          'reading_play': 1.0,
                          'reaction_to_losing_ball': 1.25,
                          'ball_control': 2.0,
                          'receiving_under_pressure': 2.0,
                          'twisting_turning': 2.0,
                          'one_v_one_dominance': 1.5,
                          'dribbling': 1.75,
                          'passing_range': 1.25,
                          'passing_quality': 2.0,
                          'attacking_heading': 1.0,
                          'crossing': 2.0,
                          'finishing': 1.5,
                          'hard_to_beat': 1.0,
                          'defensive_heading': 1.0,
                          'tackling': 1.0,
                          'interceptions': 1.0,
                          'competitive_edge': 1.0,
                          'bravery_on_ball': 2.0,
                          'bravery_without_ball': 1.5,
                          'control': 1.0,
                          'concentration': 1.0,
                          'communication': 1.0},
'striker_goalscorer': {'finding_space': 2.0,
                       'vision': 1.0,
                       'decision_making': 2.0,
                       'support_play': 1.25,
                       'reading_play': 1.0,
                       'reaction_to_losing_ball': 1.25,
                       'ball_control': 1.5,
                       'receiving_under_pressure': 1.25,
                       'twisting_turning': 1.5,
                       'one_v_one_dominance': 1.25,
                       'dribbling': 1.25,
                       'passing_range': 1.0,
                       'passing_quality': 1.0,
                       'attacking_heading': 2.0,
                       'crossing': 1.0,
                       'finishing': 2.0,
                       'hard_to_beat': 1.0,
                       'defensive_heading': 1.0,
                       'tackling': 1.0,
                       'interceptions': 1.0,
                       'competitive_edge': 2.0,
                       'bravery_on_ball': 1.5,
                       'bravery_without_ball': 1.5,
                       'control': 1.75,
                       'concentration': 2.0,
                       'communication': 1.0},
'striker_target_player': {'finding_space': 1.75,
                          'vision': 1.0,
                          'decision_making': 1.5,
                          'support_play': 1.5,
                          'reading_play': 1.0,
                          'reaction_to_losing_ball': 1.25,
                          'ball_control': 1.5,
                          'receiving_under_pressure': 1.25,
                          'twisting_turning': 2.0,
                          'one_v_one_dominance': 1.5,
                          'dribbling': 1.25,
                          'passing_range': 1.0,
                          'passing_quality': 1.0,
                          'attacking_heading': 2.0,
                          'crossing': 1.0,
                          'finishing': 2.0,
                          'hard_to_beat': 1.0,
                          'defensive_heading': 1.5,
                          'tackling': 1.0,
                          'interceptions': 1.0,
                          'competitive_edge': 2.0,
                          'bravery_on_ball': 1.5,
                          'bravery_without_ball': 1.5,
                          'control': 1.25,
                          'concentration': 1.5,
                          'communication': 1.0}}

POSITION_PHYSICAL_WEIGHTS = {'goalkeeper': {'height_cm': 2.0, 'sprint_5m_seconds': 1.75, 'sprint_30m_seconds': 1.5, 'vo2max': 1.25},
 'center_back_dominant': {'height_cm': 2.0, 'sprint_5m_seconds': 1.5, 'sprint_30m_seconds': 1.5, 'vo2max': 1.5},
 'center_back_ballplaying': {'height_cm': 1.75, 'sprint_5m_seconds': 1.5, 'sprint_30m_seconds': 1.5, 'vo2max': 1.75},
 'full_back_offensive': {'height_cm': 1.25, 'sprint_5m_seconds': 2.0, 'sprint_30m_seconds': 2.0, 'vo2max': 2.0},
 'full_back_defensive': {'height_cm': 1.5, 'sprint_5m_seconds': 1.75, 'sprint_30m_seconds': 1.75, 'vo2max': 1.75},
 'defensive_midfielder_deep_playmaker': {'height_cm': 1.5,
                                         'sprint_5m_seconds': 1.5,
                                         'sprint_30m_seconds': 1.5,
                                         'vo2max': 2.0},
 'defensive_midfielder_holding': {'height_cm': 1.75,
                                  'sprint_5m_seconds': 1.75,
                                  'sprint_30m_seconds': 1.5,
                                  'vo2max': 2.0},
 'central_midfielder_box_to_box': {'height_cm': 1.25,
                                   'sprint_5m_seconds': 1.75,
                                   'sprint_30m_seconds': 1.75,
                                   'vo2max': 2.0},
 'attacking_midfielder_playmaker': {'height_cm': 1.25,
                                    'sprint_5m_seconds': 1.5,
                                    'sprint_30m_seconds': 1.5,
                                    'vo2max': 1.75},
 'attacking_midfielder_shadow_striker': {'height_cm': 1.5,
                                         'sprint_5m_seconds': 1.75,
                                         'sprint_30m_seconds': 2.0,
                                         'vo2max': 1.75},
 'winger_classic': {'height_cm': 1.25, 'sprint_5m_seconds': 2.0, 'sprint_30m_seconds': 2.0, 'vo2max': 2.0},
 'winger_wide_playmaker': {'height_cm': 1.25, 'sprint_5m_seconds': 1.75, 'sprint_30m_seconds': 2.0, 'vo2max': 1.75},
 'striker_goalscorer': {'height_cm': 1.5, 'sprint_5m_seconds': 2.0, 'sprint_30m_seconds': 2.0, 'vo2max': 1.75},
 'striker_target_player': {'height_cm': 2.0, 'sprint_5m_seconds': 1.5, 'sprint_30m_seconds': 1.5, 'vo2max': 1.75}}


def _valid_score(value: Any) -> bool:
    """True for finite numeric ratings on the app's 1-10 scale."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return isfinite(value) and 1 <= value <= 10


def _weighted_score(
    values: Mapping[str, Any], weights: Mapping[str, int | float]
) -> dict[str, Any]:
    """Weighted mean and weighted coverage, excluding absent/invalid values."""
    applicable_weight = sum(float(w) for w in weights.values() if w and w > 0)
    if applicable_weight <= 0:
        return {"score": None, "coverage": None, "present_weight": 0.0, "total_weight": 0.0, "details": {}}

    present_weight = 0.0
    weighted_total = 0.0
    details = {}
    for code, raw_weight in weights.items():
        weight = float(raw_weight or 0)
        if weight <= 0:
            continue
        value = values.get(code)
        valid = _valid_score(value)
        details[code] = {"score": float(value) if valid else None, "weight": weight, "included": valid}
        if valid:
            weighted_total += float(value) * weight
            present_weight += weight

    score = weighted_total / present_weight if present_weight else None
    return {
        "score": round(score, 2) if score is not None else None,
        "coverage": round(present_weight / applicable_weight * 100, 1),
        "present_weight": present_weight,
        "total_weight": applicable_weight,
        "details": details,
    }


def score_position_fit(
    attribute_scores: Mapping[str, Any],
    position: str,
    physical_scores: Mapping[str, Any] | None = None,
    category_weights: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Calculate a role-fit score from existing 1-10 trait and normalized physical scores.

    Args:
        attribute_scores: Mapping of existing scoring.py attribute codes to 1-10 values.
        position: A key from POSITION_LABELS, e.g. ``center_back_dominant``.
        physical_scores: Optional normalized 1-10 scores keyed by PHYSICAL_METRICS.
            These are not raw measurements; raw-data normalization needs agreed norms.
        category_weights: Optional overrides for tactical/technical/behaviour/physical.

    Missing values are excluded from each weighted mean, never treated as zero.
    Zero profile weights mean the trait is not role-defining. Category weights are
    renormalized across categories that have a valid score. Coverage remains based
    on all categories configured for that role, so missing data remains visible.
    Goalkeeper football-trait weights are intentionally undefined in the source
    matrix; the function therefore returns no overall fit score for that role.
    """
    if position not in POSITION_LABELS:
        raise ValueError(f"Unknown position profile: {position!r}. Choose from: {', '.join(POSITION_LABELS)}")

    weights = dict(CATEGORY_WEIGHTS)
    if category_weights is not None:
        unknown = set(category_weights) - set(weights)
        if unknown:
            raise ValueError(f"Unknown category weight(s): {', '.join(sorted(unknown))}")
        weights.update({k: float(v) for k, v in category_weights.items()})
        if any(not isfinite(v) or v < 0 for v in weights.values()) or sum(weights.values()) <= 0:
            raise ValueError("Category weights must be finite, non-negative, and not all zero.")

    role_weights = POSITION_TRAIT_WEIGHTS[position]
    physical_weights = POSITION_PHYSICAL_WEIGHTS[position]
    categories = {}
    for category in ("tactical", "technical", "behaviour"):
        category_role_weights = {
            code: role_weights[code]
            for code, code_category in ATTRIBUTE_CATEGORIES.items()
            if code_category == category and role_weights.get(code, 0) > 0
        }
        categories[category] = _weighted_score(attribute_scores, category_role_weights)

    physical_scores = physical_scores or {}
    categories["physical"] = _weighted_score(physical_scores, physical_weights)

    # A completely blank football role profile (currently goalkeeper) must not
    # produce a misleading overall score from physical measurements alone.
    game_profile_defined = any(role_weights.get(code, 0) > 0 for code in ATTRIBUTE_CATEGORIES)
    available_categories = {
        name: item["score"] for name, item in categories.items()
        if item["score"] is not None and weights[name] > 0
    }
    available_game_categories = {
        name: categories[name]["score"]
        for name in ("tactical", "technical", "behaviour")
        if categories[name]["score"] is not None and weights[name] > 0
    }
    if game_profile_defined and available_game_categories and available_categories:
        active_weight = sum(weights[name] for name in available_categories)
        overall = sum(score * weights[name] for name, score in available_categories.items()) / active_weight
        overall = round(overall, 2)
    else:
        # Physical data alone must not masquerade as a full role-fit result.
        overall = None

    # Weighted data coverage across categories defined for this role.
    configured_categories = []
    for name, item in categories.items():
        if name == "physical":
            is_configured = any(w > 0 for w in physical_weights.values())
        else:
            is_configured = any(
                ATTRIBUTE_CATEGORIES[code] == name and role_weights.get(code, 0) > 0
                for code in ATTRIBUTE_CATEGORIES
            )
        if is_configured and weights[name] > 0:
            configured_categories.append(name)
    coverage_denominator = sum(weights[name] for name in configured_categories)
    coverage = (
        sum(weights[name] * (categories[name]["coverage"] or 0) / 100 for name in configured_categories)
        / coverage_denominator * 100
        if coverage_denominator else 0.0
    )

    trait_details = []
    for code, detail in categories["tactical"]["details"].items():
        trait_details.append((code, detail))
    for category in ("technical", "behaviour"):
        trait_details.extend(categories[category]["details"].items())
    scored_traits = [
        {"code": code, "score": detail["score"], "weight": detail["weight"], "weighted_contribution": detail["score"] * detail["weight"]}
        for code, detail in trait_details if detail["included"]
    ]
    scored_traits.sort(key=lambda item: item["score"], reverse=True)

    return {
        "position": position,
        "position_label": POSITION_LABELS[position],
        "overall_score": overall,
        "coverage_percent": round(coverage, 1),
        "categories": categories,
        "top_strengths": scored_traits[:5],
        "development_areas": list(reversed(scored_traits[-5:])),
        "game_profile_defined": game_profile_defined,
        "notes": (["A kapus futballszakmai súlyai nincsenek meghatározva a forrásmátrixban; az összesített illeszkedési pontszám ezért nem számítható."] if not game_profile_defined else []),
    }


def rank_positions(
    attribute_scores: Mapping[str, Any],
    physical_scores: Mapping[str, Any] | None = None,
    positions: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Rank profiles by overall score, leaving profiles without one at the end."""
    selected = positions or list(POSITION_LABELS)
    results = [score_position_fit(attribute_scores, pos, physical_scores) for pos in selected]
    return sorted(results, key=lambda result: (result["overall_score"] is not None, result["overall_score"] or -1), reverse=True)
