# apps/performance/scoring.py

"""
Performance & Potential scoring engine.

26 performance attributes:
- 6 Tactical
- 14 Technical
- 6 Behaviour

+ 26 attribute-level Potential ratings, with legacy category-level fallback
  for historical assessments only.

All ratings are on a 1-10 scale.
"""

from statistics import mean


# ============================================================
# QUESTION BANK
# ============================================================

TACTICAL_QUESTIONS = [
    {
        "code": "finding_space",
        "name": "Helyezkedés / üres terület keresése",
        "statement": (
            "Képes felismerni és elfoglalni a szabad területeket, "
            "hogy megjátszható legyen, helyzetet teremtsen vagy segítse a játékot."
        ),
        "phase": "attacking"
    },
    {
        "code": "vision",
        "name": "Játéklátás",
        "statement": (
            "Képes felismerni a társak és az ellenfelek pozícióját és "
            "a játék továbbépítésének lehetőségeit."
        ),
        "phase": "attacking"
    },
    {
        "code": "decision_making",
        "name": "Döntéshozatal",
        "statement": (
            "Hatékony döntéseket hoz még a labda átvétele előtt, "
            "illetve labdabirtoklás közben."
        ),
        "phase": "attacking"
    },
    {
        "code": "support_play",
        "name": "Támogató játék",
        "statement": (
            "Felismeri, mikor és hova kell mozognia ahhoz, "
            "hogy támogassa a labdás játékost."
        ),
        "phase": "attacking"
    },
    {
        "code": "reading_play",
        "name": "Játék olvasása",
        "statement": (
            "Képes előre felismerni, mi fog történni a következő "
            "játékhelyzetben a labda, a társak és az ellenfelek mozgása alapján."
        ),
        "phase": "defending"
    },
    {
        "code": "reaction_to_losing_ball",
        "name": "Reakció labdavesztés után",
        "statement": (
            "Labdavesztés után megfelelően reagál: azonnal nyomást "
            "gyakorol vagy megfelelően visszarendeződik."
        ),
        "phase": "defending"
    },
]


TECHNICAL_QUESTIONS = [
    {
        "code": "ball_control",
        "name": "Labdaátvétel / labdakontroll",
        "statement": (
            "Első érintése minőségi, és úgy veszi át a labdát, "
            "hogy azzal előkészítse a következő játékhelyzetet."
        ),
        "phase": "attacking"
    },
    {
        "code": "receiving_under_pressure",
        "name": "Labdaátvétel nyomás alatt",
        "statement": (
            "Nyomás alatt is képes hatékonyan átvenni és kontrollálni "
            "a labdát, megfelelő testhelyzetet és első érintést használva."
        ),
        "phase": "attacking"
    },
    {
        "code": "twisting_turning",
        "name": "Fordulás és labda megőrzése",
        "statement": (
            "Képes megvédeni a labdát, manipulálni az ellenfelet "
            "és nyomás alatt is megtartani a labdabirtoklást."
        ),
        "phase": "attacking"
    },
    {
        "code": "one_v_one_dominance",
        "name": "1v1 dominancia",
        "statement": (
            "Képes sebesség-, mozgás- és ritmusváltással megverni "
            "ellenfelét és előnyt kialakítani 1v1 helyzetben."
        ),
        "phase": "attacking"
    },
    {
        "code": "dribbling",
        "name": "Labdavezetés",
        "statement": (
            "Különböző sebességnél és irányváltásoknál is "
            "szoros kontroll alatt tartja a labdát."
        ),
        "phase": "attacking"
    },
    {
        "code": "passing_range",
        "name": "Passzolási távolság",
        "statement": (
            "Rövid, közepes és hosszú távolságra is hatékonyan "
            "képes passzolni (A magas pontszámhoz mindháromnak teljesülnie kell)."
        ),
        "phase": "attacking"
    },
    {
        "code": "passing_quality",
        "name": "Passzolási minőség",
        "statement": (
            "A megfelelő pontossággal, erővel, időzítéssel és irányba "
            "választja és hajtja végre a passzokat."
        ),
        "phase": "attacking"
    },
    {
        "code": "attacking_heading",
        "name": "Támadó fejelés kapura",
        "statement": (
            "Megfelelő időzítéssel, pontossággal és erővel "
            "támadja a labdát a kapu felé."
        ),
        "phase": "attacking"
    },
    {
        "code": "crossing",
        "name": "Beadás",
        "statement": (
            "Pontos és veszélyes beadásokat képes végrehajtani "
            "a szélső pozíciókból."
        ),
        "phase": "attacking"
    },
    {
        "code": "finishing",
        "name": "Befejezés",
        "statement": (
            "Különböző helyzetekből, távolságokból és szögekből "
            "is pontosan és hatékonyan fejez be."
        ),
        "phase": "attacking"
    },
    {
        "code": "hard_to_beat",
        "name": "1v1 védekezésben",
        "statement": (
            "Türelemmel, agresszivitással és fegyelemmel képes "
            "megakadályozni az ellenfelet az előrejutásban 1v1 helyzetben."
        ),
        "phase": "defending"
    },
    {
        "code": "defensive_heading",
        "name": "Védekező fejelés",
        "statement": (
            "Pontosan, megfelelő erővel és irányba képes védekező "
            "fejest végrehajtani a veszély megszüntetésére a posztjának megfelelően."
        ),
        "phase": "defending"
    },
    {
        "code": "tackling",
        "name": "Szerelés",
        "statement": (
            "Felismeri a megfelelő pillanatot a szerelésre, "
            "és biztonságosan, hatékonyan szerez labdát."
        ),
        "phase": "defending"
    },
    {
        "code": "interceptions",
        "name": "Labdaszerzés / közbeavatkozás",
        "statement": (
            "Képes előre olvasni a passzokat és mozgásokat, "
            "hogy közbeavatkozással labdát szerezzen."
        ),
        "phase": "defending"
    },
]


BEHAVIOUR_QUESTIONS = [
    {
        "code": "competitive_edge",
        "name": "Versenyszellem",
        "statement": (
            "Szeret versenyezni, párharcokat nyerni és pozitív hatást "
            "gyakorolni a játékra, az eredménytől függetlenül."
        ),
        "phase": "mentality"
    },
    {
        "code": "bravery_on_ball",
        "name": "Bátorság labdával",
        "statement": (
            "Nyomás alatt is kéri, megjátssza és vállalja a labdát, "
            "és bízik saját döntéseiben."
        ),
        "phase": "mentality"
    },
    {
        "code": "bravery_without_ball",
        "name": "Bátorság labda nélkül",
        "statement": (
            "Labda nélkül is hajlandó védekezni, presszingelni, "
            "szerelni és a csapat érdekeit az egyéni szempontok elé helyezni."
        ),
        "phase": "mentality"
    },
    {
        "code": "control",
        "name": "Érzelemkontroll",
        "statement": (
            "Megőrzi a nyugalmát, kezeli az érzelmeit és nyomás alatt "
            "is képes tiszta döntéseket hozni."
        ),
        "phase": "mentality"
    },
    {
        "code": "concentration",
        "name": "Koncentráció",
        "statement": (
            "A mérkőzés során végig fókuszált, éber és aktív marad, "
            "akkor is, ha nem aktív szereplője a játéknak."
        ),
        "phase": "mentality"
    },
    {
        "code": "communication",
        "name": "Kommunikáció",
        "statement": (
            "Világos, céltudatos és megfelelő időben történő verbális "
            "és nonverbális kommunikációval támogatja társait."
        ),
        "phase": "mentality"
    },
]


# Potential is rated for each existing attribute, using the same 1–10 scale.
# The statement is shared, while the form explains the context for each dimension.
POTENTIAL_QUESTIONS = [
    {
        **question,
        "code": f"potential_{question['code']}",
        "performance_code": question["code"],
    }
    for question in (
        TACTICAL_QUESTIONS + TECHNICAL_QUESTIONS + BEHAVIOUR_QUESTIONS
    )
]


# ============================================================
# QUESTION GROUPS
# ============================================================

ALL_PERFORMANCE_QUESTIONS = (
    TACTICAL_QUESTIONS
    + TECHNICAL_QUESTIONS
    + BEHAVIOUR_QUESTIONS
)

ALL_QUESTIONS = ALL_PERFORMANCE_QUESTIONS + POTENTIAL_QUESTIONS


# ============================================================
# VALIDATION
# ============================================================

def validate_rating(value):
    """
    Validate a single 1-10 rating.

    Returns:
        float: validated rating
    """

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError("A pontszámnak 1 és 10 közötti számnak kell lennie.")

    if value < 1 or value > 10:
        raise ValueError("A pontszámnak 1 és 10 között kell lennie.")

    return value


def validate_assessment(scores):
    """Validate that a new assessment contains all 52 ratings."""
    required_codes = [q["code"] for q in ALL_QUESTIONS]
    missing = [code for code in required_codes if code not in scores or scores[code] in (None, "")]
    if missing:
        raise ValueError(f"Hiányzó értékelések: {', '.join(missing)}")
    for code in required_codes:
        validate_rating(scores[code])
    return True


# ============================================================
# SCORING
# ============================================================

def _average(scores, questions):
    """
    Calculate the average score of a question group.
    """

    values = [
        validate_rating(scores[q["code"]])
        for q in questions
    ]

    return round(mean(values), 2)


def calculate_scores(scores):
    """
    Calculate all performance and potential scores.

    Returns a dictionary containing:

        tactical
        technical
        behaviour
        performance

        tactical_potential
        technical_potential
        behavioural_potential
        potential
    """

    # Historical records may only have the previous three category-level
    # Potential scores. New assessment submissions are still validated strictly
    # by validate_assessment() in the POST route.
    performance_questions = TACTICAL_QUESTIONS + TECHNICAL_QUESTIONS + BEHAVIOUR_QUESTIONS
    for question in performance_questions:
        if question["code"] not in scores or scores[question["code"]] in (None, ""):
            raise ValueError(f"Hiányzó Performance-értékelés: {question['code']}")
        validate_rating(scores[question["code"]])

    potential_codes = [q["code"] for q in POTENTIAL_QUESTIONS]
    present_potential = [
        code for code in potential_codes
        if code in scores and scores[code] not in (None, "")
    ]

    tactical = _average(scores, TACTICAL_QUESTIONS)
    technical = _average(scores, TECHNICAL_QUESTIONS)
    behaviour = _average(scores, BEHAVIOUR_QUESTIONS)

    # Phase subscores are derived from the canonical question-bank metadata.
    # Keep category (tactical/technical) and phase (attacking/defending)
    # separate; mentality remains its own behavioural phase.
    tactical_attacking = _average(
        scores, [q for q in TACTICAL_QUESTIONS if q.get("phase") == "attacking"]
    )
    tactical_defending = _average(
        scores, [q for q in TACTICAL_QUESTIONS if q.get("phase") == "defending"]
    )
    technical_attacking = _average(
        scores, [q for q in TECHNICAL_QUESTIONS if q.get("phase") == "attacking"]
    )
    technical_defending = _average(
        scores, [q for q in TECHNICAL_QUESTIONS if q.get("phase") == "defending"]
    )

    # Important:
    # Tactical, Technical and Behaviour each have equal weight
    # in the Overall Performance score.
    performance = round(
        mean([tactical, technical, behaviour]),
        2
    )

    if len(present_potential) == len(potential_codes):
        potential_tactical = _average(scores, [
            {**question, "code": f"potential_{question['code']}"}
            for question in TACTICAL_QUESTIONS
        ])
        potential_technical = _average(scores, [
            {**question, "code": f"potential_{question['code']}"}
            for question in TECHNICAL_QUESTIONS
        ])
        potential_behaviour = _average(scores, [
            {**question, "code": f"potential_{question['code']}"}
            for question in BEHAVIOUR_QUESTIONS
        ])
        potential_source = "attribute"
    elif not present_potential:
        legacy_keys = [
            "tactical_potential",
            "technical_potential",
            "behavioural_potential",
        ]
        if not all(scores.get(key) not in (None, "") for key in legacy_keys):
            raise ValueError(
                "Ehhez az értékeléshez nincs teljes Potential-adat. "
                "A régi értékelést újra kell értékelni."
            )
        potential_tactical = validate_rating(scores["tactical_potential"])
        potential_technical = validate_rating(scores["technical_potential"])
        potential_behaviour = validate_rating(scores["behavioural_potential"])
        potential_source = "legacy_category"
    else:
        raise ValueError("Az értékelés csak részleges Potential-adatokat tartalmaz.")

    # Equal weighting of the three main areas, matching Performance.
    potential = round(mean([potential_tactical, potential_technical, potential_behaviour]), 2)

    return {
        "tactical": tactical,
        "technical": technical,
        "behaviour": behaviour,
        "performance": performance,
        "tactical_attacking": tactical_attacking,
        "tactical_defending": tactical_defending,
        "technical_attacking": technical_attacking,
        "technical_defending": technical_defending,
        "tactical_potential": potential_tactical,
        "technical_potential": potential_technical,
        "behavioural_potential": potential_behaviour,
        "potential": potential,
        "potential_source": potential_source,
    }


# ============================================================
# HELPERS
# ============================================================

def get_question(code):
    """
    Return a question by its code.
    """

    for question in ALL_QUESTIONS:
        if question["code"] == code:
            return question

    return None


def get_questions_by_category(category):
    """
    Return questions belonging to a category.

    Supported:
        tactical
        technical
        behaviour
        potential (all 26 attribute-level Potential ratings)
    """

    category = category.lower()

    if category == "tactical":
        return TACTICAL_QUESTIONS

    if category == "technical":
        return TECHNICAL_QUESTIONS

    if category == "behaviour":
        return BEHAVIOUR_QUESTIONS

    if category == "potential":
        return POTENTIAL_QUESTIONS

    raise ValueError(f"Ismeretlen kategória: {category}")


def question_count():
    """
    Return the number of questions.
    """

    return {
        "tactical": len(TACTICAL_QUESTIONS),
        "technical": len(TECHNICAL_QUESTIONS),
        "behaviour": len(BEHAVIOUR_QUESTIONS),
        "performance": len(ALL_PERFORMANCE_QUESTIONS),
        "potential": len(POTENTIAL_QUESTIONS),
        "total": len(ALL_QUESTIONS),
    }
