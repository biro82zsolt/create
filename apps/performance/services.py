# apps/performance/services.py

import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Assessment
from .scoring import calculate_scores
from .mapping import get_mapping_category
from .profiles import analyze_profiles, get_profile_details
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    KeepInFrame,
    PageBreak,
    Flowable,
)
from reportlab.lib.units import inch, mm
from xml.sax.saxutils import escape

import matplotlib
from .mapping import get_mapping_grid

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from reportlab.platypus import Image
from .constants import PERFORMANCE_ATTRIBUTES

RATING_FIELDS = [
    "finding_space",
    "vision",
    "decision_making",
    "support_play",
    "reading_play",
    "reaction_to_losing_ball",
    "ball_control",
    "receiving_under_pressure",
    "twisting_turning",
    "one_v_one_dominance",
    "dribbling",
    "passing_range",
    "passing_quality",
    "attacking_heading",
    "crossing",
    "finishing",
    "hard_to_beat",
    "defensive_heading",
    "tackling",
    "interceptions",
    "competitive_edge",
    "bravery_on_ball",
    "bravery_without_ball",
    "control",
    "concentration",
    "communication",
    "potential_finding_space",
    "potential_vision",
    "potential_decision_making",
    "potential_support_play",
    "potential_reading_play",
    "potential_reaction_to_losing_ball",
    "potential_ball_control",
    "potential_receiving_under_pressure",
    "potential_twisting_turning",
    "potential_one_v_one_dominance",
    "potential_dribbling",
    "potential_passing_range",
    "potential_passing_quality",
    "potential_attacking_heading",
    "potential_crossing",
    "potential_finishing",
    "potential_hard_to_beat",
    "potential_defensive_heading",
    "potential_tackling",
    "potential_interceptions",
    "potential_competitive_edge",
    "potential_bravery_on_ball",
    "potential_bravery_without_ball",
    "potential_control",
    "potential_concentration",
    "potential_communication",
]

FONT_DIR = os.path.join(
        os.path.dirname(__file__),
        "static",
        "fonts",
    )

pdfmetrics.registerFont(
        TTFont(
            "DejaVuSans",
            os.path.join(FONT_DIR, "DejaVuSans.ttf"),
        )
    )

pdfmetrics.registerFont(
        TTFont(
            "DejaVuSans-Bold",
            os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"),
        )
    )


def assessment_to_ratings(assessment):
    """Return the 52 attribute-level ratings stored on an assessment."""
    return {field: getattr(assessment, field) for field in RATING_FIELDS}



def analyze_assessment(assessment):
    """
    Egy Assessment teljes kiértékelése.

    Visszaadja:
    - részpontszámokat
    - Performance értéket
    - Potential értéket
    - Performance × Potential mappinget
    - profilpontszámokat
    - archetype-ot
    - elsődleges és másodlagos profilt
    """

    ratings = assessment_to_ratings(assessment)

    # ---------------------------------------------------------
    # SCORING
    # ---------------------------------------------------------

    scores = calculate_scores(ratings)

    # ---------------------------------------------------------
    # PERFORMANCE × POTENTIAL MAPPING
    # ---------------------------------------------------------

    mapping = (
        get_mapping_category(scores["performance"], scores["potential"])
        if scores.get("potential") is not None
        else None
    )

    # ---------------------------------------------------------
    # PLAYER PROFILE
    # ---------------------------------------------------------

    profile_analysis = analyze_profiles(ratings)

    archetype = profile_analysis["archetype"]

    primary_code = profile_analysis["primary"]
    secondary_code = profile_analysis.get("secondary")

    primary_details = get_profile_details(primary_code)

    secondary_details = None

    if secondary_code:
        secondary_details = get_profile_details(secondary_code)

    # ---------------------------------------------------------
    # RESULT
    # ---------------------------------------------------------

    return {
        "scores": scores,

        "mapping": mapping,

        "profiles": {
            "type": archetype["type"],
            "type_hu": archetype["type_hu"],
            "difference": archetype["difference"],

            "primary": {
                "code": primary_code,
                "name": primary_details,
            },

            "secondary": (
                {
                    "code": secondary_code,
                    "name": secondary_details,
                }
                if secondary_code
                else None
            ),

            "scores": profile_analysis["scores"],
        },
    }

# ---------------------------------------------------------
# AGGREGATED PLAYER RESULT
# ---------------------------------------------------------

def aggregate_assessments(assessments):
    """
    Több edzői értékelésből összesített eredményt készít.

    Az egyes Assessment rekordok változatlanul megmaradnak.
    Az aggregáció csak eredmény-megjelenítési célra készül.
    """

    if not assessments:
        return None

    results = [
        analyze_assessment(assessment)
        for assessment in assessments
    ]

    score_keys = [
        "tactical",
        "technical",
        "behaviour",
        "performance",
        "tactical_potential",
        "technical_potential",
        "behavioural_potential",
        "potential",
        "tactical_attacking",
        "tactical_defending",
        "technical_attacking",
        "technical_defending",
    ]

    aggregated_scores = {}

    for key in score_keys:
        values = [
            result["scores"][key]
            for result in results
        ]

        available_values = [value for value in values if value is not None]
        aggregated_scores[key] = (
            round(sum(available_values) / len(available_values), 2)
            if available_values
            else None
        )

    # -----------------------------------------------------
    # AGGREGATED MAPPING
    # -----------------------------------------------------

    mapping = (
        get_mapping_category(
            aggregated_scores["performance"],
            aggregated_scores["potential"],
        )
        if aggregated_scores["potential"] is not None
        else None
    )

    # -----------------------------------------------------
    # PROFILE
    # -----------------------------------------------------

    # A profilokat az egyes értékelésekből számítjuk,
    # majd azok profilpontszámait átlagoljuk.

    profile_codes = [
        "athlete",
        "warrior",
        "builder",
        "dribbler",
        "playmaker",
        "finisher",
    ]

    profile_scores = {}

    for code in profile_codes:

        values = [
            result["profiles"]["scores"][code]
            for result in results
        ]

        profile_scores[code] = round(
            sum(values) / len(values),
            2,
        )

    sorted_profiles = sorted(
        profile_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    primary_code = sorted_profiles[0][0]

    secondary_code = (
        sorted_profiles[1][0]
        if len(sorted_profiles) > 1
        else None
    )

    difference = round(
        sorted_profiles[0][1]
        - sorted_profiles[1][1],
        2,
    )

    if difference >= 0.50:
        archetype_type = "clear"
        archetype_type_hu = "Egyértelmű profil"

    elif difference >= 0.25:
        archetype_type = "hybrid"
        archetype_type_hu = "Hibrid profil"

    else:
        archetype_type = "versatile"
        archetype_type_hu = "Sokoldalú profil"

    # -----------------------------------------------------
    # AGGREGATED ATTRIBUTE SCORES
    # -----------------------------------------------------

    aggregated_attributes = {}

    for field in RATING_FIELDS:
        values = [
            getattr(assessment, field)
            for assessment in assessments
        ]

        aggregated_attributes[field] = round(
            sum(values) / len(values),
            2,
        )

    return {
        "assessment_count": len(assessments),

        "attributes": aggregated_attributes,

        "scores": aggregated_scores,

        "mapping": mapping,

        "profiles": {
            "type": archetype_type,
            "type_hu": archetype_type_hu,
            "difference": difference,

            "primary": {
                "code": primary_code,
                "name": get_profile_details(
                    primary_code
                ),
            },

            "secondary": (
                {
                    "code": secondary_code,
                    "name": get_profile_details(
                        secondary_code
                    ),
                }
                if secondary_code
                else None
            ),

            "scores": profile_scores,
        },
    }

def calculate_team_averages(team_id, period_id):
    """
    Csapatátlagok számítása egy adott értékelési időszakra.

    A számítás játékosszinten történik:
    - először az adott játékos összes edzői értékelésének átlaga,
    - majd ezekből számolunk csapatátlagot.

    Így egy játékos két edzői értékelése nem számít kétszer
    annyit a csapatátlagba, mint egy másik játékos egy értékelése.
    """

    from .models import Assessment

    assessments = (
        Assessment.query
        .filter_by(
            team_id=team_id,
            period_id=period_id,
        )
        .order_by(Assessment.player_id)
        .all()
    )

    if not assessments:
        return None

    # Értékelések csoportosítása játékosonként
    player_assessments = {}

    for assessment in assessments:
        player_assessments.setdefault(
            assessment.player_id,
            []
        ).append(assessment)

    # Játékosszintű átlagok
    player_ratings = {}

    for player_id, player_assessment_list in player_assessments.items():
        ratings = {}

        for field in RATING_FIELDS:
            values = [
                getattr(assessment, field)
                for assessment in player_assessment_list
            ]

            ratings[field] = sum(values) / len(values)

        player_ratings[player_id] = ratings

    # Csapatszintű attribútumátlagok
    team_attributes = {}

    for field in RATING_FIELDS:
        values = [
            ratings[field]
            for ratings in player_ratings.values()
        ]

        team_attributes[field] = round(
            sum(values) / len(values),
            2,
        )

    # A három fő kategória és Performance / Potential
    team_scores = calculate_scores(team_attributes)

    return {
        "player_count": len(player_ratings),
        "assessment_count": len(assessments),
        "attributes": team_attributes,
        "scores": team_scores,
    }

def calculate_age_group_averages(birth_year, period_id):
    """
    Korosztályátlag számítása születési év és értékelési időszak alapján.

    Egy játékos több edzői értékelése először játékosszinten átlagolódik,
    majd a játékosok egyenlő súllyal szerepelnek a korosztályátlagban.
    """

    from .models import Player, Assessment

    players = (
        Player.query
        .filter(
            Player.birth_date.isnot(None),
            Player.active.is_(True),
        )
        .all()
    )

    player_ids = [
        player.id
        for player in players
        if player.birth_date.year == int(birth_year)
    ]

    if not player_ids:
        return None

    assessments = (
        Assessment.query
        .filter(
            Assessment.player_id.in_(player_ids),
            Assessment.period_id == period_id,
        )
        .all()
    )

    if not assessments:
        return None

    player_assessments = {}

    for assessment in assessments:
        player_assessments.setdefault(
            assessment.player_id,
            [],
        ).append(assessment)

    player_ratings = {}

    for player_id, assessment_list in player_assessments.items():
        ratings = {}

        for field in RATING_FIELDS:
            values = [
                getattr(assessment, field)
                for assessment in assessment_list
            ]

            ratings[field] = sum(values) / len(values)

        player_ratings[player_id] = ratings

    age_group_attributes = {}

    for field in RATING_FIELDS:
        values = [
            ratings[field]
            for ratings in player_ratings.values()
        ]

        age_group_attributes[field] = round(
            sum(values) / len(values),
            2,
        )

    age_group_scores = calculate_scores(age_group_attributes)

    return {
        "birth_year": int(birth_year),
        "player_count": len(player_ratings),
        "assessment_count": len(assessments),
        "attributes": age_group_attributes,
        "scores": age_group_scores,
    }



PERFORMANCE_FIELDS = [
    "finding_space",
    "vision",
    "decision_making",
    "support_play",
    "reading_play",
    "reaction_to_losing_ball",

    "ball_control",
    "receiving_under_pressure",
    "twisting_turning",
    "one_v_one_dominance",
    "dribbling",
    "passing_range",
    "passing_quality",
    "attacking_heading",
    "crossing",
    "finishing",
    "hard_to_beat",
    "defensive_heading",
    "tackling",
    "interceptions",

    "competitive_edge",
    "bravery_on_ball",
    "bravery_without_ball",
    "control",
    "concentration",
    "communication",
]


def calculate_player_insights(
    player_attributes,
    team_attributes,
    attributes=None,
):
    if attributes is None:
        attributes = PERFORMANCE_ATTRIBUTES
    """
    A játékos és a korosztályátlag közötti eltérések alapján
    meghatározza a fő erősségeket és fejlesztési területeket.
    """

    differences = []

    for label, code, _ in attributes:
        player_value = player_attributes.get(code)
        team_value = team_attributes.get(code)

        if player_value is None or team_value is None:
            continue

        difference = round(
            player_value - team_value,
            2,
        )

        differences.append({
            "label": label,
            "code": code,
            "player_value": round(player_value, 2),
            "team_value": round(team_value, 2),
            "difference": difference,
        })

    strengths = sorted(
        [
            item
            for item in differences
            if item["difference"] > 0
        ],
        key=lambda item: item["difference"],
        reverse=True,
    )[:3]

    development_areas = sorted(
        [
            item
            for item in differences
            if item["difference"] < 0
        ],
        key=lambda item: item["difference"],
    )[:3]

    return {
        "strengths": strengths,
        "development_areas": development_areas,
    }

def _average(assessment, fields):
    values = [
        getattr(assessment, field)
        for field in fields
        if getattr(assessment, field) is not None
    ]

    if not values:
        return 0

    return sum(values) / len(values)

def generate_performance_potential_chart(
    aggregated,
    team_averages,
):
    """
    Performance × Potential scatter chart.

    A player_detail.html chartjának PDF-kompatibilis változata.
    """

    aggregated_scores = aggregated.get("scores", {})

    performance = aggregated_scores.get("performance")
    potential = aggregated_scores.get("potential")

    team_performance = None
    team_potential = None

    if team_averages:
        team_scores = team_averages.get("scores", {})

        team_performance = team_scores.get("performance")
        team_potential = team_scores.get("potential")

    figure, axis = plt.subplots(
        figsize=(6.5, 5.2),
        dpi=160,
    )

    # Játékos pontja
    if performance is not None and potential is not None:
        axis.scatter(
            performance,
            potential,
            s=130,
            label="Játékos",
            zorder=3,
        )

        axis.annotate(
            "Játékos",
            (performance, potential),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=9,
        )

    # Korosztályos átlag
    if (
        team_performance is not None
        and team_potential is not None
    ):
        axis.scatter(
            team_performance,
            team_potential,
            s=110,
            marker="X",
            label="Korosztályos átlag",
            zorder=3,
        )

        axis.annotate(
            "Korosztályos átlag",
            (team_performance, team_potential),
            xytext=(8, -14),
            textcoords="offset points",
            fontsize=8,
        )

    # Tengelyek
    axis.set_xlim(1, 10)
    axis.set_ylim(1, 10)

    axis.set_xlabel("Performance")
    axis.set_ylabel("Potential")

    axis.set_title(
        "Performance × Potential",
        fontsize=12,
        fontweight="bold",
    )

    axis.set_xticks(range(1, 11))
    axis.set_yticks(range(1, 11))

    axis.grid(
        True,
        linestyle="--",
        alpha=0.35,
    )

    axis.legend(
        loc="lower right",
        fontsize=8,
    )

    figure.tight_layout()

    chart_buffer = BytesIO()

    figure.savefig(
        chart_buffer,
        format="png",
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(figure)

    chart_buffer.seek(0)

    return chart_buffer


class RotatedLabel(Flowable):
    """90 fokkal elforgatott tengelyfelirat."""

    def __init__(self, text, style, width=18, height=160):
        super().__init__()
        self.text = text
        self.style = style
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        self.canv.translate(self.width / 2, self.height / 2)
        self.canv.rotate(90)

        paragraph = Paragraph(self.text, self.style)
        text_width, text_height = paragraph.wrap(
            self.height,
            self.width,
        )
        paragraph.drawOn(
            self.canv,
            -text_width / 2,
            -text_height / 2,
        )

        self.canv.restoreState()


def build_mapping_grid(mapping_grid, active_code, styles):
    """
    Build the 3×3 Performance × Potential mapping grid for PDF.
    """

    cell_data = []


    for row in mapping_grid:

        pdf_row = []

        for cell in row:

            code = cell["code"]
            name = cell["name_hu"]

            is_active = code == active_code

            border_color = (
                HexColor("#111827")
                if is_active
                else HexColor("#d1d5db")
            )

            border_width = 2 if is_active else 0.5

            cell_style = ParagraphStyle(
                f"mapping_{code}",
                parent=styles["normal"],
                fontName="DejaVuSans-Bold",
                fontSize=8,
                leading=10,
                alignment=1,
                textColor=HexColor("#111827"),
            )

            content = name

            if is_active:
                content += "<br/><font size='6'>● Jelenlegi kategória</font>"

            pdf_cell = Table(
                [[Paragraph(content, cell_style)]],
                colWidths=[52 * mm],
                rowHeights=[22 * mm],
            )

            pdf_cell.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        HexColor(
                            cell.get("color", "#f3f4f6")
                            ),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        border_width,
                        border_color,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ])
            )

            pdf_row.append(pdf_cell)

        cell_data.append(pdf_row)

    grid_table = Table(
        cell_data,
        colWidths=[52 * mm] * 3,
        rowHeights=[22 * mm] * 3,
        hAlign="CENTER",
    )

    grid_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )


    # Tengelyfeliratok hozzáadása a mapping rácshoz
    x_label = Paragraph(
        "<b>PERFORMANCE →</b>",
        ParagraphStyle(
            "MappingXAxis",
            parent=styles["normal"],
            fontName="DejaVuSans-Bold",
            fontSize=9,
            alignment=1,
        ),
    )

    y_label = RotatedLabel(
        "POTENTIAL →",
        ParagraphStyle(
            "MappingYAxis",
            parent=styles["normal"],
            fontName="DejaVuSans-Bold",
            fontSize=9,
            alignment=1,
        ),
    )

    mapping_with_axes = Table(
        [
            [y_label, grid_table],
            ["", x_label],
        ],
        colWidths=[65, 468],
    )

    mapping_with_axes.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("SPAN", (1, 0), (1, 0)),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )

    return mapping_with_axes

def generate_radar_chart(assessments, team_averages):
    """
    26 attribútumos radar diagram generálása.
    Játékosátlag + korosztályátlag.
    """

    import matplotlib.pyplot as plt
    import numpy as np

    attributes = [
        ("Helyezkedés", "finding_space"),
        ("Játéklátás", "vision"),
        ("Döntéshozatal", "decision_making"),
        ("Támogatójáték", "support_play"),
        ("Játék olvasása", "reading_play"),
        ("Labdavesztés reakció", "reaction_to_losing_ball"),

        ("Labdakontroll", "ball_control"),
        ("Átvétel nyomás alatt", "receiving_under_pressure"),
        ("Fordulás / irányváltás", "twisting_turning"),
        ("1v1 dominancia", "one_v_one_dominance"),
        ("Cselezés", "dribbling"),
        ("Passzterjedelem", "passing_range"),
        ("Passzminőség", "passing_quality"),
        ("Támadó fejjáték", "attacking_heading"),
        ("Beadás", "crossing"),
        ("Befejezés", "finishing"),
        ("Nehéz átjátszani", "hard_to_beat"),
        ("Védekező fejjáték", "defensive_heading"),
        ("Szerelés", "tackling"),
        ("Labdaszerzés", "interceptions"),

        ("Versenyszellem", "competitive_edge"),
        ("Bátorság labdával", "bravery_on_ball"),
        ("Bátorság labda nélkül", "bravery_without_ball"),
        ("Kontroll", "control"),
        ("Koncentráció", "concentration"),
        ("Kommunikáció", "communication"),
    ]

    labels = [item[0] for item in attributes]
    codes = [item[1] for item in attributes]

    # Játékos átlagos attribútumértékei
    player_values = []

    for code in codes:
        values = [
            getattr(assessment, code)
            for assessment in assessments
            if getattr(assessment, code) is not None
        ]

        player_values.append(
            sum(values) / len(values)
            if values
            else 0
        )

    # Korosztályátlag
    team_values = [
        (team_averages or {}).get("attributes", {}).get(code, 0)
        for code in codes
    ]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False,
    )

    player_values += player_values[:1]
    team_values += team_values[:1]
    angles = np.concatenate((angles, [angles[0]]))

    fig, ax = plt.subplots(
        figsize=(10, 9),
        subplot_kw={"polar": True},
    )

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        labels,
        fontsize=9,
    )

    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(
        ["2", "4", "6", "8", "10"],
        fontsize=7,
    )

    ax.plot(
        angles,
        player_values,
        linewidth=2,
        label="Játékos",
    )

    ax.fill(
        angles,
        player_values,
        alpha=0.15,
    )

    if team_averages:
        ax.plot(
            angles,
            team_values,
            linewidth=1.5,
            linestyle="--",
            label="Korosztályátlag",
        )

    ax.set_title(
        "Teljesítményprofil",
        fontsize=14,
        fontweight="bold",
        pad=25,
    )

    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=2,
    )

    fig.tight_layout()

    chart_buffer = BytesIO()

    fig.savefig(
        chart_buffer,
        format="png",
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    chart_buffer.seek(0)

    return chart_buffer

def generate_player_pdf(
    player,
    aggregated,
    team_averages,
    assessments,
    insights=None,
):
    """
    A játékos adatlapjának PDF-generálása.

    Az adatlap vizuális logikáját követő, A4-es PDF:
    - játékos fejléc
    - Performance / Potential
    - Performance × Potential mapping
    - radar chart
    - teljesítménykategóriák
    - játékosprofil
    - erősségek / fejlesztési területek
    - egyéni edzői értékelések
    - edzői megjegyzések

    A mapping és a radar chart egyetlen, nem törhető blokkot alkot.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=32,
        leftMargin=32,
        topMargin=32,
        bottomMargin=32,
    )

    styles = getSampleStyleSheet()

    # -------------------------------------------------
    # STÍLUSOK
    # -------------------------------------------------

    title_style = ParagraphStyle(
        "PlayerTitle",
        parent=styles["Title"],
        fontName="DejaVuSans-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "PlayerSubtitle",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#6b7280"),
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="DejaVuSans-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#111827"),
        spaceBefore=10,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#374151"),
    )

    small_style = ParagraphStyle(
        "Small",
        parent=normal_style,
        fontSize=7.5,
        leading=9.5,
    )

    score_style = ParagraphStyle(
        "Score",
        parent=styles["Normal"],
        fontName="DejaVuSans-Bold",
        fontSize=22,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
    )

    score_label_style = ParagraphStyle(
        "ScoreLabel",
        parent=styles["Normal"],
        fontName="DejaVuSans-Bold",
        fontSize=6.5,
        leading=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#6b7280"),
    )

    white_small_style = ParagraphStyle(
        "WhiteSmall",
        parent=small_style,
        textColor=colors.white,
    )

    story = []

    # -------------------------------------------------
    # SEGÉDVÁLTOZÓK
    # -------------------------------------------------

    aggregated_scores = aggregated.get("scores", {})
    aggregated_profiles = aggregated.get("profiles", {})
    aggregated_mapping = aggregated.get("mapping", {})

    average_scores = {}

    if team_averages:
        average_scores = team_averages.get("scores", {})

    def format_score(value):
        if value is None:
            return "-"
        return f"{float(value):.2f}"

    def safe_text(value):
        if value is None:
            return "-"
        return str(value)

    def cell_text(value, style=normal_style):
        return Paragraph(
            escape(safe_text(value)),
            style,
        )

    # -------------------------------------------------
    # FEJLÉC
    # -------------------------------------------------

    player_name = safe_text(player.full_name)

    player_meta = (
        f"{safe_text(player.team.name if player.team else '-')}"
        f" · #{safe_text(player.player_code)}"
    )

    if player.birth_date:
        player_meta += (
            f" · {player.birth_date.strftime('%Y-%m-%d')}"
        )

    # Mérési időszak neve
    period_name = "-"

    if assessments:
        first_item = assessments[0]
        assessment = first_item.get("assessment")

        if assessment and assessment.period:
            period_name = safe_text(assessment.period.name)

    player_meta += f" · {period_name}"

    header_left = [
        Paragraph(
            player_name,
            title_style,
        ),
        Paragraph(
            player_meta,
            subtitle_style,
        ),
    ]

    performance_score = format_score(
        aggregated_scores.get("performance")
    )

    potential_score = format_score(
        aggregated_scores.get("potential")
    )

    performance_box = Table(
        [
            [
                Paragraph(
                    "PERFORMANCE",
                    score_label_style,
                )
            ],
            [
                Paragraph(
                    performance_score,
                    score_style,
                )
            ],
        ],
        colWidths=[78],
    )

    performance_box.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#f3f4f6"),
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                colors.HexColor("#d1d5db"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )

    potential_box = Table(
        [
            [
                Paragraph(
                    "POTENTIAL",
                    score_label_style,
                )
            ],
            [
                Paragraph(
                    potential_score,
                    score_style,
                )
            ],
        ],
        colWidths=[78],
    )

    potential_box.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#f3f4f6"),
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                colors.HexColor("#d1d5db"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )

    score_boxes = Table(
        [
            [
                performance_box,
                potential_box,
            ]
        ],
        colWidths=[78, 78],
    )

    score_boxes.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                2,
            ),
        ])
    )

    header_table = Table(
        [
            [
                header_left,
                score_boxes,
            ]
        ],
        colWidths=[334, 166],
    )

    header_table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "ALIGN",
                (1, 0),
                (1, 0),
                "RIGHT",
            ),
            (
                "LINEBELOW",
                (0, 0),
                (-1, -1),
                1,
                colors.HexColor("#e5e7eb"),
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),
        ])
    )

    story.append(header_table)
    story.append(Spacer(1, 12))

    # -------------------------------------------------
    # FŐ TELJESÍTMÉNYTERÜLETEK
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Fő teljesítményterületek",
            section_style,
        )
    )

    category_rows = [
        ["Részterület", "Játékos", "Csapatátlag"],
        [
            "Taktika – védekezés",
            format_score(aggregated_scores.get("tactical_defending")),
            format_score(average_scores.get("tactical_defending")),
        ],
        [
            "Taktika – támadás",
            format_score(aggregated_scores.get("tactical_attacking")),
            format_score(average_scores.get("tactical_attacking")),
        ],
        [
            "Technika – védekezés",
            format_score(aggregated_scores.get("technical_defending")),
            format_score(average_scores.get("technical_defending")),
        ],
        [
            "Technika – támadás",
            format_score(aggregated_scores.get("technical_attacking")),
            format_score(average_scores.get("technical_attacking")),
        ],
        [
            "Mentalitás",
            format_score(aggregated_scores.get("behaviour")),
            format_score(average_scores.get("behaviour")),
        ],
    ]

    category_table = Table(
        category_rows,
        colWidths=[245, 125, 130],
    )

    category_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1f4e79"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "DejaVuSans-Bold",
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "DejaVuSans",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#d1d5db"),
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
        ])
    )

    story.append(category_table)

    # -------------------------------------------------
    # JÁTÉKOSPROFIL
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Játékosprofil",
            section_style,
        )
    )

    primary_data = (
            aggregated_profiles.get("primary") or {}
    )

    secondary_data = (
            aggregated_profiles.get("secondary") or {}
    )

    primary_details = (
            primary_data.get("name") or {}
    )

    secondary_details = (
            secondary_data.get("name") or {}
    )

    primary_profile = primary_details.get(
        "name_hu",
        "-"
    )

    primary_description = primary_details.get(
        "description",
        "-"
    )

    secondary_profile = secondary_details.get(
        "name_hu",
        "-"
    )

    secondary_description = secondary_details.get(
        "description",
        "-"
    )

    mapping_name = (
        aggregated_mapping.get(
            "name_hu",
            "-"
        )
        if aggregated_mapping
        else "-"
    )

    mapping_description = (
        aggregated_mapping.get(
            "description",
            "-"
        )
        if aggregated_mapping
        else "-"
    )

    profile_data = [
        [
            cell_text("Mapping"),
            cell_text(mapping_name),
        ],
        [
            cell_text("Mapping értelmezése"),
            cell_text(mapping_description),
        ],
        [
            cell_text("Profil típusa"),
            cell_text(
                aggregated_profiles.get(
                    "type_hu"
                )
            ),
        ],
        [
            cell_text("Elsődleges profil"),
            cell_text(primary_profile),
        ],
        [
            cell_text(
                "Elsődleges profil leírása"
            ),
            cell_text(primary_description),
        ],
        [
            cell_text("Másodlagos profil"),
            cell_text(secondary_profile),
        ],
        [
            cell_text(
                "Másodlagos profil leírása"
            ),
            cell_text(secondary_description),
        ],
    ]

    profile_table = Table(
        profile_data,
        colWidths=[155, 345],
    )

    profile_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#d1d5db"),
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#f3f4f6"),
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "DejaVuSans",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7.8,
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
        ])
    )

    story.append(profile_table)

    story.append(PageBreak())


    # -------------------------------------------------
    # MAPPING
    # -------------------------------------------------

    mapping_grid = get_mapping_grid()

    active_mapping_code = (
        aggregated_mapping.get("code")
        if aggregated_mapping
        else None
    )

    mapping_table = build_mapping_grid(
        mapping_grid=mapping_grid,
        active_code=active_mapping_code,
        styles={
            "normal": small_style,
        },
    )

    # -------------------------------------------------
    # RADAR
    # -------------------------------------------------

    radar_buffer = generate_radar_chart(
        assessments=[
            item["assessment"]
            for item in assessments
        ],
        team_averages=team_averages,
    )

    radar_image = Image(
        radar_buffer,
        width=245,
        height=222,
    )


    # -------------------------------------------------
    # MAPPING + RADAR BLOKK - EGYMÁS ALATT
    # -------------------------------------------------

    mapping_heading = Paragraph(
        "Performance × Potential",
        section_style,
    )

    mapping_subtitle = Paragraph(
        "Játékos pozíciója a 9 kategóriás modellben",
        small_style,
    )


    radar_heading = Paragraph(
        "Teljesítményprofil",
        section_style,
    )

    radar_subtitle = Paragraph(
        "Játékos és korosztályátlag · 26 teljesítményattribútum",
        small_style,
    )

    # A mapping teljes szélességben, zsugorítás nélkül,
    # amennyiben az oldal szélessége ezt lehetővé teszi.
    mapping_frame = KeepInFrame(
        maxWidth=500,
        maxHeight=230,
        content=[mapping_table],
        mode="shrink",
    )

    story.append(mapping_heading)
    story.append(mapping_subtitle)
    story.append(Spacer(1, 6))
    story.append(mapping_frame)
    story.append(Spacer(1, 12))

    # Nagyobb radar diagram, teljes szélességben.
    radar_image = Image(
        radar_buffer,
        width=450,
        height=405,
    )

    story.append(PageBreak())
    story.append(radar_heading)
    story.append(radar_subtitle)
    story.append(Spacer(1, 4))
    story.append(
        KeepTogether([
            radar_image,
        ])
    )

    story.append(Spacer(1, 10))


    # -------------------------------------------------
    # ERŐSSÉGEK / FEJLESZTÉSI TERÜLETEK
    # -------------------------------------------------

    strengths = (
        insights.get("strengths", [])
        if insights
        else []
    )

    development_areas = (
        insights.get("development_areas", [])
        if insights
        else []
    )

    if strengths or development_areas:

        story.append(
            Paragraph(
                "Erősségek és fejlesztési területek",
                section_style,
            )
        )

        insight_data = [
            [
                Paragraph(
                    "ERŐSSÉGEK",
                    white_small_style,
                ),
                Paragraph(
                    "FEJLESZTÉSI TERÜLETEK",
                    white_small_style,
                ),
            ]
        ]

        max_items = max(
            len(
                insights.get(
                    "strengths",
                    []
                )
            ),
            len(
                insights.get(
                    "development_areas",
                    []
                )
            ),
        )

        strength_items = insights.get(
            "strengths",
            []
        )

        development_items = insights.get(
            "development_areas",
            []
        )

        for index in range(max_items):

            strength = (
                strength_items[index]
                if index < len(strength_items)
                else None
            )

            development = (
                development_areas[index]
                if index < len(development_areas)
                else None
            )

            def format_insight(item):
                if not item:
                    return "-"

                return (
                    f"<b>{escape(item['label'])}</b><br/>"
                    f"Játékos: "
                    f"{item['player_value']:.2f}"
                    f" · Korosztály: "
                    f"{item['team_value']:.2f}"
                    f"<br/>"
                    f"Eltérés: "
                    f"{item['difference']:+.2f}"
                )

            insight_data.append(
                [
                    Paragraph(
                        format_insight(strength),
                        normal_style,
                    ),
                    Paragraph(
                        format_insight(development),
                        normal_style,
                    ),
                ]
            )

        insight_table = Table(
            insight_data,
            colWidths=[250, 250],
        )

        insight_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f4e79"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#d1d5db"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ])
        )

        story.append(insight_table)

    # -------------------------------------------------
    # EGYÉNI EDZŐI ÉRTÉKELÉSEK
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Egyéni edzői értékelések",
            section_style,
        )
    )

    assessment_data = [
        [
            "Értékelési időszak",
            "Értékelő",
            "Dátum",
            "Performance",
            "Potential",
        ]
    ]

    for item in assessments:

        assessment = item["assessment"]
        result = item["result"]

        assessment_data.append([
            (
                assessment.period.name
                if assessment.period
                else "-"
            ),
            (
                assessment.coach.name
                if assessment.coach
                else "-"
            ),
            (
                assessment.completed_at.strftime(
                    "%Y-%m-%d"
                )
                if assessment.completed_at
                else "-"
            ),
            format_score(
                result.get(
                    "scores",
                    {}
                ).get("performance")
            ),
            format_score(
                result.get(
                    "scores",
                    {}
                ).get("potential")
            ),
        ])

    assessment_table = Table(
        assessment_data,
        colWidths=[
            120,
            120,
            80,
            90,
            90,
        ],
        repeatRows=1,
    )

    assessment_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1f4e79"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "DejaVuSans-Bold",
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "DejaVuSans",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#d1d5db"),
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6.5,
            ),
        ])
    )

    story.append(assessment_table)

    # -------------------------------------------------
    # EDZŐI MEGJEGYZÉSEK
    # -------------------------------------------------

    notes_added = False

    for item in assessments:

        assessment = item["assessment"]

        if assessment.coach_note:

            if not notes_added:
                story.append(
                    Paragraph(
                        "Edzői megjegyzések",
                        section_style,
                    )
                )

                notes_added = True

            story.append(
                Table(
                    [
                        [
                            Paragraph(
                                safe_text(
                                    assessment.coach_note
                                ),
                                normal_style,
                            )
                        ]
                    ],
                    colWidths=[500],
                    style=TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor("#f9fafb"),
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor("#d1d5db"),
                        ),
                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                    ]),
                )
            )

            story.append(Spacer(1, 6))

    # -------------------------------------------------
    # GENERÁLÁS DÁTUMA
    # -------------------------------------------------

    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            (
                "Generálva: "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ),
            small_style,
        )
    )

    # -------------------------------------------------
    # PDF GENERÁLÁSA
    # -------------------------------------------------

    document.build(story)

    buffer.seek(0)

    return buffer
