from io import BytesIO
from datetime import datetime

import pandas as pd

from .models import (
    Team,
    Player,
    Coach,
    AssessmentPeriod,
    Assessment,
)

from .services import analyze_assessment


# ---------------------------------------------------------
# ASSESSMENT RAW FIELDS
# ---------------------------------------------------------

RAW_ASSESSMENT_FIELDS = [
    # Tactical
    "finding_space",
    "vision",
    "decision_making",
    "support_play",
    "reading_play",
    "reaction_to_losing_ball",

    # Technical
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

    # Behaviour
    "competitive_edge",
    "bravery_on_ball",
    "bravery_without_ball",
    "control",
    "concentration",
    "communication",

    # Potential
    "tactical_potential",
    "technical_potential",
    "behavioural_potential",

    # Extra
    "coach_note",
]


# ---------------------------------------------------------
# ASSESSMENT EXPORT
# ---------------------------------------------------------

def create_assessments_dataframe():

    assessments = (
        Assessment.query
        .order_by(Assessment.completed_at)
        .all()
    )

    rows = []

    for assessment in assessments:

        player = assessment.player
        team = assessment.team
        coach = assessment.coach
        period = assessment.period

        row = {
            # -------------------------------------------------
            # AZONOSÍTÓ ADATOK
            # -------------------------------------------------

            "assessment_id": assessment.id,

            "player_id": player.id if player else None,

            "player_code": (
                player.player_code
                if player
                else None
            ),

            "last_name": (
                player.last_name
                if player
                else None
            ),

            "first_name": (
                player.first_name
                if player
                else None
            ),

            "team_id": team.id if team else None,

            "team_name": (
                team.name
                if team
                else None
            ),

            "coach_id": coach.id if coach else None,

            "coach_name": (
                coach.name
                if coach
                else None
            ),

            "period_id": period.id if period else None,

            "period_name": (
                period.name
                if period
                else None
            ),

            "completed_at": assessment.completed_at,
        }

        # -------------------------------------------------
        # NYERS PONTSZÁMOK
        # -------------------------------------------------

        for field in RAW_ASSESSMENT_FIELDS:

            row[field] = getattr(
                assessment,
                field,
                None,
            )

        # -------------------------------------------------
        # SZÁMÍTOTT EREDMÉNYEK
        # -------------------------------------------------

        try:

            result = analyze_assessment(assessment)

            scores = result["scores"]

            row.update({
                "tactical": scores["tactical"],
                "technical": scores["technical"],
                "behaviour": scores["behaviour"],
                "performance": scores["performance"],

                "tactical_potential": (
                    scores["tactical_potential"]
                ),

                "technical_potential": (
                    scores["technical_potential"]
                ),

                "behavioural_potential": (
                    scores["behavioural_potential"]
                ),

                "potential": scores["potential"],
            })

            # -------------------------------------------------
            # MAPPING
            # -------------------------------------------------

            mapping = result["mapping"]

            row.update({
                "mapping_code": mapping.get("code"),
                "mapping_name": mapping.get("name"),
                "mapping_name_hu": mapping.get("name_hu"),

                "performance_level": (
                    mapping.get("performance_level")
                ),

                "potential_level": (
                    mapping.get("potential_level")
                ),
            })

            # -------------------------------------------------
            # PROFILE / ARCHETYPE
            # -------------------------------------------------

            profiles = result["profiles"]

            row.update({
                "archetype_type": profiles.get("type"),
                "archetype_type_hu": profiles.get("type_hu"),
                "profile_difference": profiles.get("difference"),
            })

            primary = profiles.get("primary") or {}
            secondary = profiles.get("secondary") or {}

            primary_name = primary.get("name") or {}
            secondary_name = secondary.get("name") or {}

            row.update({
                "primary_profile_code": (
                    primary.get("code")
                ),

                "primary_profile_name": (
                    primary_name.get("name")
                    if isinstance(primary_name, dict)
                    else None
                ),

                "primary_profile_name_hu": (
                    primary_name.get("name_hu")
                    if isinstance(primary_name, dict)
                    else None
                ),

                "secondary_profile_code": (
                    secondary.get("code")
                ),

                "secondary_profile_name": (
                    secondary_name.get("name")
                    if isinstance(secondary_name, dict)
                    else None
                ),

                "secondary_profile_name_hu": (
                    secondary_name.get("name_hu")
                    if isinstance(secondary_name, dict)
                    else None
                ),
            })

            # Profilpontszámok

            profile_scores = profiles.get("scores") or {}

            for profile_code, profile_score in profile_scores.items():

                row[
                    f"profile_{profile_code}"
                ] = profile_score

        except Exception as exc:

            # Az export ne álljon le egy hibás értékelés miatt

            row["calculation_error"] = str(exc)

        rows.append(row)

    return pd.DataFrame(rows)

# ---------------------------------------------------------
# COMPLETE BACKUP
# ---------------------------------------------------------

def create_backup_excel():

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        # Players
        players = Player.query.all()

        player_rows = []

        for player in players:

            player_rows.append({
                "id": player.id,
                "player_code": player.player_code,
                "last_name": player.last_name,
                "first_name": player.first_name,
                "birth_date": player.birth_date,
                "team_id": player.team_id,
                "team_name": (
                    player.team.name
                    if player.team
                    else None
                ),
                "active": player.active,
                "created_at": player.created_at,
            })

        pd.DataFrame(player_rows).to_excel(
            writer,
            sheet_name="Players",
            index=False,
        )

        # Teams
        teams = Team.query.all()

        pd.DataFrame([
            {
                "id": team.id,
                "name": team.name,
                "created_at": team.created_at,
            }
            for team in teams
        ]).to_excel(
            writer,
            sheet_name="Teams",
            index=False,
        )

        # Team relationships
        relationship_rows = []

        for player in players:

            for team in player.roster_teams:

                relationship_rows.append({
                    "player_id": player.id,
                    "team_id": team.id,
                })

        pd.DataFrame(
            relationship_rows
        ).to_excel(
            writer,
            sheet_name="Team_Relationships",
            index=False,
        )

        # Coaches
        coaches = Coach.query.all()

        pd.DataFrame([
            {
                "id": coach.id,
                "name": coach.name,
                "email": coach.email,
                "created_at": coach.created_at,
            }
            for coach in coaches
        ]).to_excel(
            writer,
            sheet_name="Coaches",
            index=False,
        )

        # Assessment periods
        periods = AssessmentPeriod.query.all()

        pd.DataFrame([
            {
                "id": period.id,
                "name": period.name,
                "start_date": period.start_date,
                "end_date": period.end_date,
                "created_at": period.created_at,
            }
            for period in periods
        ]).to_excel(
            writer,
            sheet_name="Assessment_Periods",
            index=False,
        )

        # Assessments with raw scores
        assessments_df = create_assessments_dataframe()

        assessments_df.to_excel(
            writer,
            sheet_name="Assessments",
            index=False,
        )

    output.seek(0)

    return output