# apps/performance/profiles.py

"""
Player Profile / Archetype Engine

Profiles:
    Athlete
    Warrior
    Builder
    Dribbler
    Playmaker
    Finisher

The engine calculates:
    1. Absolute profile score (1-10)
    2. Profile ranking
    3. Profile dominance
    4. Archetype type:
       - CLEAR
       - HYBRID
       - VERSATILE
"""


# ============================================================
# PROFILE RULES
# ============================================================

PROFILE_RULES = {

    "athlete": {
        "name": "Athlete",
        "name_hu": "Atléta",
        "description": (
            "Intenzív, aktív játékos, aki mozgásával, aktivitásával "
            "és labda nélküli munkájával jelentős hatást gyakorol a játékra."
        ),
        "attributes": {
            "reaction_to_losing_ball": 1.8,
            "competitive_edge": 1.6,
            "bravery_without_ball": 1.5,
            "support_play": 1.4,
            "finding_space": 1.3,
            "concentration": 1.2,
            "communication": 0.8,
        },
    },

    "warrior": {
        "name": "Warrior",
        "name_hu": "Harcos",
        "description": (
            "Párharcerős, versengő és bátor játékos, aki különösen "
            "a nehéz és intenzív játékhelyzetekben képes hatást gyakorolni."
        ),
        "attributes": {
            "competitive_edge": 2.0,
            "bravery_without_ball": 1.8,
            "tackling": 1.8,
            "hard_to_beat": 1.7,
            "bravery_on_ball": 1.4,
            "interceptions": 1.3,
            "reaction_to_losing_ball": 1.2,
        },
    },

    "builder": {
        "name": "Builder",
        "name_hu": "Játéképítő",
        "description": (
            "A játék felépítésében, összekapcsolásában és a csapat "
            "játékstruktúrájának támogatásában erős játékos."
        ),
        "attributes": {
            "reading_play": 2.0,
            "vision": 1.8,
            "decision_making": 1.7,
            "support_play": 1.7,
            "passing_quality": 1.6,
            "passing_range": 1.4,
            "finding_space": 1.2,
            "ball_control": 1.0,
            "communication": 1.0,
        },
    },

    "dribbler": {
        "name": "Dribbler",
        "name_hu": "Cselező",
        "description": (
            "Labdával képes egyéni előnyt kialakítani, különösen "
            "1v1 helyzetekben és szűk területeken."
        ),
        "attributes": {
            "dribbling": 2.2,
            "one_v_one_dominance": 2.0,
            "twisting_turning": 1.8,
            "receiving_under_pressure": 1.4,
            "ball_control": 1.4,
            "bravery_on_ball": 1.3,
            "decision_making": 0.8,
        },
    },

    "playmaker": {
        "name": "Playmaker",
        "name_hu": "Irányító",
        "description": (
            "A játékot látja, értelmezi és irányítja. Erőssége a "
            "játéklátás, a döntéshozatal és a megfelelő megoldások felismerése."
        ),
        "attributes": {
            "vision": 2.0,
            "decision_making": 2.0,
            "reading_play": 1.8,
            "passing_quality": 1.8,
            "passing_range": 1.4,
            "support_play": 1.3,
            "ball_control": 1.0,
            "communication": 1.0,
        },
    },

    "finisher": {
        "name": "Finisher",
        "name_hu": "Befejező",
        "description": (
            "A támadások végső szakaszában különösen veszélyes játékos, "
            "aki képes helyzetbe kerülni és hatékonyan befejezni."
        ),
        "attributes": {
            "finishing": 2.2,
            "finding_space": 1.8,
            "one_v_one_dominance": 1.5,
            "attacking_heading": 1.4,
            "bravery_on_ball": 1.2,
            "ball_control": 1.0,
            "crossing": 0.8,
        },
    },
}


# ============================================================
# VALIDATION
# ============================================================

def validate_score(value):
    """
    Validate an individual performance attribute.
    """

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            "A profilértéknek 1 és 10 közötti számnak kell lennie."
        )

    if value < 1 or value > 10:
        raise ValueError(
            "A profilértéknek 1 és 10 között kell lennie."
        )

    return value


# ============================================================
# SINGLE PROFILE
# ============================================================

def calculate_profile_score(scores, profile_code):
    """
    Calculate the weighted score for one profile.

    Returns:
        float between 1 and 10
    """

    if profile_code not in PROFILE_RULES:
        raise ValueError(
            f"Ismeretlen profil: {profile_code}"
        )

    rules = PROFILE_RULES[profile_code]["attributes"]

    weighted_sum = 0.0
    total_weight = 0.0

    for attribute, weight in rules.items():

        if attribute not in scores:
            raise ValueError(
                f"Hiányzó attribútum: {attribute}"
            )

        value = validate_score(scores[attribute])

        weighted_sum += value * weight
        total_weight += weight

    return round(weighted_sum / total_weight, 2)


# ============================================================
# ALL PROFILE SCORES
# ============================================================

def calculate_profiles(scores):
    """
    Calculate all six profile scores.

    Returns:
        Dictionary sorted from highest to lowest.
    """

    results = {}

    for profile_code in PROFILE_RULES:

        results[profile_code] = calculate_profile_score(
            scores,
            profile_code
        )

    return dict(
        sorted(
            results.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


# ============================================================
# PROFILE DIFFERENCE
# ============================================================

def get_profile_difference(profiles):
    """
    Difference between the first and second highest profiles.
    """

    profile_codes = list(profiles.keys())

    if len(profile_codes) < 2:
        return None

    first_score = profiles[profile_codes[0]]
    second_score = profiles[profile_codes[1]]

    return round(first_score - second_score, 2)


# ============================================================
# ARCHETYPE CLASSIFICATION
# ============================================================

def classify_archetype(profiles):
    """
    Classify the player based on the distance between
    the strongest profiles.

    Rules:

        difference >= 0.50
            CLEAR PROFILE

        difference 0.25 - 0.49
            HYBRID

        difference < 0.25
            VERSATILE
    """

    profile_codes = list(profiles.keys())

    if len(profile_codes) < 2:
        raise ValueError(
            "Legalább két profil szükséges a besoroláshoz."
        )

    first = profile_codes[0]
    second = profile_codes[1]

    first_score = profiles[first]
    second_score = profiles[second]

    difference = round(
        first_score - second_score,
        2
    )

    if difference >= 0.50:

        return {
            "type": "clear",
            "type_hu": "Egyértelmű profil",
            "primary": first,
            "secondary": None,
            "difference": difference,
        }

    if difference >= 0.25:

        return {
            "type": "hybrid",
            "type_hu": "Hibrid profil",
            "primary": first,
            "secondary": second,
            "difference": difference,
        }

    return {
        "type": "versatile",
        "type_hu": "Sokoldalú profil",
        "primary": first,
        "secondary": second,
        "difference": difference,
    }


# ============================================================
# COMPLETE PROFILE RESULT
# ============================================================

def analyze_profiles(scores):
    """
    Calculate the complete player profile analysis.

    Returns:

        scores
        ranking
        archetype
        primary
        secondary
    """

    profiles = calculate_profiles(scores)

    archetype = classify_archetype(profiles)

    primary = archetype["primary"]
    secondary = archetype["secondary"]

    return {
        "scores": profiles,
        "archetype": archetype,
        "primary": primary,
        "secondary": secondary,
    }


# ============================================================
# PROFILE DETAILS
# ============================================================

def get_profile_details(profile_code):
    """
    Return metadata for a profile.
    """

    return PROFILE_RULES.get(profile_code)


# ============================================================
# DISPLAY NAME
# ============================================================

def get_profile_name(profile_code):
    """
    Return Hungarian profile name.
    """

    profile = get_profile_details(profile_code)

    if not profile:
        return None

    return profile["name_hu"]