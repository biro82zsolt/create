# apps/performance/mapping.py

"""
Performance × Potential mapping.

Performance:
    LOW       = 1.00 - 4.99
    MEDIUM    = 5.00 - 6.99
    HIGH      = 7.00 - 10.00

Potential:
    LOW       = 1.00 - 4.99
    MEDIUM    = 5.00 - 6.99
    HIGH      = 7.00 - 10.00

The combination produces 9 player categories.
"""


# ============================================================
# PERFORMANCE / POTENTIAL LEVELS
# ============================================================

LEVELS = {
    "low": {
        "min": 1.0,
        "max": 4.99,
    },
    "medium": {
        "min": 5.0,
        "max": 6.99,
    },
    "high": {
        "min": 7.0,
        "max": 10.0,
    },
}


# ============================================================
# 9 MAPPING CATEGORIES
# ============================================================

MAPPING_CATEGORIES = {
    ("low", "low"): {
        "code": "development_risk",
        "name": "Development Risk",
        "name_hu": "Fejlődési kockázat",
        "color": "#C43D4E",
        "description": (
            "Jelenleg alacsony teljesítményt és alacsonyabb fejlődési "
            "potenciált mutat. Kiemelt támogatást, fejlesztési fókuszt "
            "és egyéni figyelmet igényel."
        ),
        "description_en": (
            "Currently demonstrates low performance and limited development "
            "potential. Requires targeted support, a clear development focus, "
            "and individual attention."
),
    },

    ("medium", "low"): {
        "code": "grafter",
        "name": "Grafter",
        "name_hu": "Dolgozó / Küzdő",
        "color": "#E05258",
        "description": (
            "A jelenlegi teljesítménye közepes, miközben a további "
            "fejlődési lehetősége korlátozottabb. Kitartó munkával "
            "és megfelelő fejlesztéssel stabil szereplővé válhat."
        ),
        "description_en": (
            "Current performance is moderate, while further development "
            "potential is more limited. With persistent effort and appropriate "
            "development, the player can become a reliable team member."
        ),
    },

    ("high", "low"): {
        "code": "overachiever",
        "name": "Overachiever",
        "name_hu": "Túlteljesítő",
        "color": "#E9C34F",
        "description": (
            "A jelenlegi teljesítménye magasabb, mint amit a fejlődési "
            "potenciálja alapján várnánk. Jelenleg nagyon produktív, "
            "de érdemes figyelni arra, hogy a teljesítménye hosszú távon "
            "is fenntartható legyen."
        ),
        "description_en": (
            "Current performance is higher than expected based on development "
            "potential. The player is highly productive at present, but it is "
            "important to ensure that this performance remains sustainable "
            "in the long term."
        ),
    },

    ("low", "medium"): {
        "code": "underperforming",
        "name": "Underperforming",
        "name_hu": "Alulteljesítő",
        "color": "#E05258",
        "description": (
            "A játékosban megvannak a szükséges képességek, de jelenleg "
            "nem teljesít a lehetőségeinek megfelelően. Érdemes feltárni "
            "a háttérben álló okokat."
        ),
        "description_en": (
            "The player has the necessary abilities but is currently not "
            "performing in line with their potential. It is worth exploring "
            "the underlying reasons."
        ),
    },

    ("medium", "medium"): {
        "code": "core_player",
        "name": "Core Player",
        "name_hu": "Stabil csapattag",
        "color": "#E9C34F",
        "description": (
            "Megbízható, kiegyensúlyozott játékos, aki jelenleg a "
            "csapat stabil középpontját jelenti. Teljesítménye és "
            "fejlődési potenciálja is közepes."
        ),
        "description_en": (
            "A reliable, well-balanced player who currently represents a "
            "stable part of the team. Both performance and development "
            "potential are moderate."
        ),
    },

    ("high", "medium"): {
        "code": "key_player",
        "name": "Key Player",
        "name_hu": "Kulcsjátékos",
        "color": "#55D6A0",
        "description": (
            "A jelenlegi teljesítménye magas, és fejlődési potenciálja "
            "is megfelelő. Fontos szerepet tölt be a csapatban, "
            "és érdemes tovább támogatni a fejlődését."
        ),
        "description_en": (
            "Current performance is high, and development potential is also "
            "promising. The player has an important role in the team and "
            "should continue to receive support for further development."
        ),
    },

    ("low", "high"): {
        "code": "rough_diamond",
        "name": "Rough Diamond",
        "name_hu": "Csiszolatlan gyémánt",
        "color": "#E9C34F",
        "description": (
            "Jelentős fejlődési potenciál látható a játékosban, "
            "de ez jelenleg még nem jelenik meg a teljesítményében. "
            "Kiemelt fejlesztési lehetőség."
        ),
        "description_en": (
            "The player shows significant development potential, but this "
            "is not yet reflected in current performance. Represents a "
            "significant development opportunity."
        ),
    },

    ("medium", "high"): {
        "code": "rising_talent",
        "name": "Rising Talent",
        "name_hu": "Feltörekvő tehetség",
        "color": "#55D6A0",
        "description": (
            "A játékosban jelentős potenciál látható, és teljesítménye "
            "már elindult felfelé. Jó fejlődési pályán van."
        ),
        "description_en": (
            "The player shows significant potential, and performance is "
            "already trending upwards. The player is on a positive "
            "development trajectory."
        ),
    },

    ("high", "high"): {
        "code": "future_star",
        "name": "Future Star",
        "name_hu": "Jövő sztárja",
        "color": "#35659A",
        "description": (
            "A játékos jelenlegi teljesítménye is magas, és jelentős "
            "fejlődési potenciál látható benne. Kiemelt figyelmet és "
            "további fejlesztést érdemel."
        ),
        "description_en": (
            "The player demonstrates high current performance and significant "
            "development potential. Deserves focused attention and continued "
            "development."
        ),
    },
}


# ============================================================
# VALIDATION
# ============================================================

def validate_score(score):
    """
    Validate a Performance or Potential score.

    Returns:
        float
    """

    try:
        score = float(score)
    except (TypeError, ValueError):
        raise ValueError(
            "A Performance és Potential pontszámnak "
            "1 és 10 közötti számnak kell lennie."
        )

    if score < 1 or score > 10:
        raise ValueError(
            "A Performance és Potential pontszámnak "
            "1 és 10 között kell lennie."
        )

    return score


# ============================================================
# LEVEL CALCULATION
# ============================================================

def get_level(score):
    """
    Convert a 1-10 score into Low / Medium / High.
    """

    score = validate_score(score)

    if score < 5:
        return "low"

    if score < 7:
        return "medium"

    return "high"


# ============================================================
# MAPPING CALCULATION
# ============================================================

def get_mapping_category(performance, potential):
    """
    Determine the player's Performance × Potential category.

    Args:
        performance: Overall Performance score, 1-10
        potential: Overall Potential score, 1-10

    Returns:
        Dictionary containing the category information.
    """

    performance = validate_score(performance)
    potential = validate_score(potential)

    performance_level = get_level(performance)
    potential_level = get_level(potential)

    category = MAPPING_CATEGORIES[
        (performance_level, potential_level)
    ]

    return {
        "performance": performance,
        "potential": potential,
        "performance_level": performance_level,
        "potential_level": potential_level,
        **category,
    }


# ============================================================
# ALL CATEGORIES
# ============================================================

def get_all_categories():
    """
    Return all 9 mapping categories.
    """

    return list(MAPPING_CATEGORIES.values())

# ============================================================
# MAPPING GRID
# ============================================================

def get_mapping_grid():
    """
    Return the 3×3 Performance × Potential mapping grid.

    Rows: Potential (HIGH → LOW)
    Columns: Performance (LOW → HIGH)
    """

    performance_levels = ["low", "medium", "high"]
    potential_levels = ["high", "medium", "low"]

    grid = []

    for potential_level in potential_levels:
        row = []

        for performance_level in performance_levels:
            category = MAPPING_CATEGORIES[
                (performance_level, potential_level)
            ]

            row.append({
                **category,
                "performance_level": performance_level,
                "potential_level": potential_level,
            })

        grid.append(row)

    return grid

# ============================================================
# CATEGORY BY CODE
# ============================================================

def get_category_by_code(code):
    """
    Return a mapping category by its code.
    """

    for category in MAPPING_CATEGORIES.values():
        if category["code"] == code:
            return category

    return None