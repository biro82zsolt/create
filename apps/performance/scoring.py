# apps/performance/scoring.py

"""
Performance & Potential scoring engine.

26 performance attributes:
- 6 Tactical
- 14 Technical
- 6 Behaviour

+ 3 Potential scores:
- Tactical Potential
- Technical Potential
- Behavioural Potential

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
        "phase": "possession"
    },
    {
        "code": "vision",
        "name": "Játéklátás",
        "statement": (
            "Képes felismerni a társak és az ellenfelek pozícióját és "
            "a játék továbbépítésének lehetőségeit."
        ),
        "phase": "possession"
    },
    {
        "code": "decision_making",
        "name": "Döntéshozatal",
        "statement": (
            "Hatékony döntéseket hoz még a labda átvétele előtt, "
            "illetve labdabirtoklás közben."
        ),
        "phase": "possession"
    },
    {
        "code": "support_play",
        "name": "Támogató játék",
        "statement": (
            "Felismeri, mikor és hova kell mozognia ahhoz, "
            "hogy támogassa a labdás játékost."
        ),
        "phase": "possession"
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
        "phase": "possession"
    },
    {
        "code": "receiving_under_pressure",
        "name": "Labdaátvétel nyomás alatt",
        "statement": (
            "Nyomás alatt is képes hatékonyan átvenni és kontrollálni "
            "a labdát, megfelelő testhelyzetet és első érintést használva."
        ),
        "phase": "possession"
    },
    {
        "code": "twisting_turning",
        "name": "Fordulás és labda megőrzése",
        "statement": (
            "Képes megvédeni a labdát, manipulálni az ellenfelet "
            "és nyomás alatt is megtartani a labdabirtoklást."
        ),
        "phase": "possession"
    },
    {
        "code": "one_v_one_dominance",
        "name": "1v1 dominancia",
        "statement": (
            "Képes sebesség-, mozgás- és ritmusváltással megverni "
            "ellenfelét és előnyt kialakítani 1v1 helyzetben."
        ),
        "phase": "possession"
    },
    {
        "code": "dribbling",
        "name": "Labdavezetés",
        "statement": (
            "Különböző sebességnél és irányváltásoknál is "
            "szoros kontroll alatt tartja a labdát."
        ),
        "phase": "possession"
    },
    {
        "code": "passing_range",
        "name": "Passzolási távolság",
        "statement": (
            "Rövid, közepes és hosszú távolságra is hatékonyan "
            "képes passzolni (A magas pontszámhoz mindháromnak teljesülnie kell)."
        ),
        "phase": "possession"
    },
    {
        "code": "passing_quality",
        "name": "Passzolási minőség",
        "statement": (
            "A megfelelő pontossággal, erővel, időzítéssel és irányba "
            "választja és hajtja végre a passzokat."
        ),
        "phase": "possession"
    },
    {
        "code": "attacking_heading",
        "name": "Támadó fejelés kapura",
        "statement": (
            "Megfelelő időzítéssel, pontossággal és erővel "
            "támadja a labdát a kapu felé."
        ),
        "phase": "possession"
    },
    {
        "code": "crossing",
        "name": "Beadás",
        "statement": (
            "Pontos és veszélyes beadásokat képes végrehajtani "
            "a szélső pozíciókból."
        ),
        "phase": "possession"
    },
    {
        "code": "finishing",
        "name": "Befejezés",
        "statement": (
            "Különböző helyzetekből, távolságokból és szögekből "
            "is pontosan és hatékonyan fejez be."
        ),
        "phase": "possession"
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


POTENTIAL_QUESTIONS = [
    {
        "code": "tactical_potential",
        "name": "Taktikai fejlődési potenciál",
        "statement": (
            "Mekkora fejlődési és tanulási potenciált látsz még "
            "a játékosban a játék olvasásában, döntéshozatalban, "
            "helyezkedésben és taktikai megértésben? Mennyire hiszel benne, "
            "hogy a játékos ezen a területen még fejlődni fog?"
        ),
    },
    {
        "code": "technical_potential",
        "name": "Technikai fejlődési potenciál",
        "statement": (
            "Mekkora fejlődési és tanulási potenciált látsz még "
            "a játékos technikai képességeiben és új technikai "
            "megoldások elsajátításában? Mennyire hiszel benne, "
            "hogy a játékos ezen a területen még fejlődni fog?"
        ),
    },
    {
        "code": "behavioural_potential",
        "name": "Viselkedési / mentális fejlődési potenciál",
        "statement": (
            "Mekkora fejlődési és tanulási potenciált látsz még "
            "a játékos hozzáállásában, önszabályozásában, "
            "koncentrációjában, kommunikációjában és a versenyhelyzetek "
            "kezelésében? Mennyire hiszel benne, "
            "hogy a játékos ezen a területen még fejlődni fog?"
        ),
    },
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
    """
    Validate that an assessment contains all 29 ratings.

    Returns:
        True if valid.

    Raises:
        ValueError if anything is missing or invalid.
    """

    required_codes = [q["code"] for q in ALL_QUESTIONS]

    missing = [
        code for code in required_codes
        if code not in scores
    ]

    if missing:
        raise ValueError(
            f"Hiányzó értékelések: {', '.join(missing)}"
        )

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

    validate_assessment(scores)

    tactical = _average(scores, TACTICAL_QUESTIONS)
    technical = _average(scores, TECHNICAL_QUESTIONS)
    behaviour = _average(scores, BEHAVIOUR_QUESTIONS)

    # Important:
    # Tactical, Technical and Behaviour each have equal weight
    # in the Overall Performance score.
    performance = round(
        mean([tactical, technical, behaviour]),
        2
    )

    tactical_potential = validate_rating(
        scores["tactical_potential"]
    )

    technical_potential = validate_rating(
        scores["technical_potential"]
    )

    behavioural_potential = validate_rating(
        scores["behavioural_potential"]
    )

    potential = round(
        mean([
            tactical_potential,
            technical_potential,
            behavioural_potential
        ]),
        2
    )

    return {
        "tactical": tactical,
        "technical": technical,
        "behaviour": behaviour,
        "performance": performance,

        "tactical_potential": round(tactical_potential, 2),
        "technical_potential": round(technical_potential, 2),
        "behavioural_potential": round(behavioural_potential, 2),
        "potential": potential,
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
        potential
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
