# apps/performance/test_scoring.py

from scoring import calculate_scores
from mapping import get_mapping_category
from profiles import analyze_profiles, get_profile_details


# ============================================================
# BASE PLAYER
# ============================================================

BASE_SCORES = {
    # Tactical
    "finding_space": 6,
    "vision": 6,
    "decision_making": 6,
    "support_play": 6,
    "reading_play": 6,
    "reaction_to_losing_ball": 6,

    # Technical
    "ball_control": 6,
    "receiving_under_pressure": 6,
    "twisting_turning": 6,
    "one_v_one_dominance": 6,
    "dribbling": 6,
    "passing_range": 6,
    "passing_quality": 6,
    "attacking_heading": 6,
    "crossing": 6,
    "finishing": 6,
    "hard_to_beat": 6,
    "defensive_heading": 6,
    "tackling": 6,
    "interceptions": 6,

    # Behaviour
    "competitive_edge": 6,
    "bravery_on_ball": 6,
    "bravery_without_ball": 6,
    "control": 6,
    "concentration": 6,
    "communication": 6,

    # Potential
    "tactical_potential": 8,
    "technical_potential": 8,
    "behavioural_potential": 8,
}


# ============================================================
# HELPER
# ============================================================

def make_player(overrides):
    """
    Create a test player from the neutral baseline.
    """

    scores = BASE_SCORES.copy()
    scores.update(overrides)

    return scores


# ============================================================
# TEST PLAYERS
# ============================================================

players = {

    "PLAYER A – CLEAR PLAYMAKER": make_player({

        # Playmaker core
        "vision": 10,
        "decision_making": 10,
        "reading_play": 9,
        "passing_quality": 10,
        "passing_range": 9,
        "support_play": 9,
        "communication": 9,
        "ball_control": 9,

        # Other areas intentionally lower
        "finishing": 5,
        "dribbling": 5,
        "one_v_one_dominance": 5,
        "tackling": 5,
        "hard_to_beat": 5,

    }),


    "PLAYER B – CLEAR FINISHER": make_player({

        # Finisher core
        "finishing": 10,
        "finding_space": 9,
        "one_v_one_dominance": 9,
        "attacking_heading": 9,
        "bravery_on_ball": 9,
        "ball_control": 9,

        # Other areas lower
        "vision": 5,
        "decision_making": 5,
        "passing_quality": 5,
        "passing_range": 5,
        "reading_play": 5,
        "tackling": 5,
        "interceptions": 5,

    }),


    "PLAYER C – WARRIOR / DRIBBLER": make_player({

        # Warrior
        "competitive_edge": 10,
        "bravery_without_ball": 10,
        "tackling": 9,
        "hard_to_beat": 9,
        "interceptions": 9,
        "reaction_to_losing_ball": 9,

        # Dribbler
        "dribbling": 10,
        "one_v_one_dominance": 10,
        "twisting_turning": 10,
        "receiving_under_pressure": 9,
        "ball_control": 9,
        "bravery_on_ball": 9,

        # Other areas moderate
        "vision": 6,
        "passing_quality": 6,
        "finishing": 6,

    }),


    "PLAYER D – ALL ROUNDER": make_player({

        # Everything good, but no dominant specialist area
        "finding_space": 8,
        "vision": 8,
        "decision_making": 8,
        "support_play": 8,
        "reading_play": 8,
        "reaction_to_losing_ball": 8,

        "ball_control": 8,
        "receiving_under_pressure": 8,
        "twisting_turning": 8,
        "one_v_one_dominance": 8,
        "dribbling": 8,
        "passing_range": 8,
        "passing_quality": 8,
        "attacking_heading": 8,
        "crossing": 8,
        "finishing": 8,
        "hard_to_beat": 8,
        "defensive_heading": 8,
        "tackling": 8,
        "interceptions": 8,

        "competitive_edge": 8,
        "bravery_on_ball": 8,
        "bravery_without_ball": 8,
        "control": 8,
        "concentration": 8,
        "communication": 8,

    }),
}


# ============================================================
# RUN TESTS
# ============================================================

for player_name, scores in players.items():

    result = calculate_scores(scores)

    mapping = get_mapping_category(
        result["performance"],
        result["potential"]
    )

    profile_analysis = analyze_profiles(scores)

    profiles = profile_analysis["scores"]
    archetype = profile_analysis["archetype"]

    print("\n")
    print("=" * 60)
    print(player_name)
    print("=" * 60)

    print("\nPERFORMANCE")
    print(f"  Tactical:    {result['tactical']}")
    print(f"  Technical:   {result['technical']}")
    print(f"  Behaviour:   {result['behaviour']}")
    print(f"  Performance: {result['performance']}")

    print("\nPOTENTIAL")
    print(f"  Potential:   {result['potential']}")

    print("\nMAPPING")
    print(f"  {mapping['name']} – {mapping['name_hu']}")

    print("\nPROFILES")

    for profile_code, score in profiles.items():

        profile = get_profile_details(profile_code)

        print(
            f"  {profile['name']:12} "
            f"{score:.2f}"
        )

    print("\nARCHETYPE")

    print(
        f"  Type:       {archetype['type_hu']}"
    )

    print(
        f"  Difference: {archetype['difference']:.2f}"
    )

    primary = get_profile_details(
        archetype["primary"]
    )

    print(
        f"  Primary:    "
        f"{primary['name']} – {primary['name_hu']}"
    )

    if archetype["secondary"]:

        secondary = get_profile_details(
            archetype["secondary"]
        )

        print(
            f"  Secondary:  "
            f"{secondary['name']} – {secondary['name_hu']}"
        )