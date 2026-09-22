from datetime import datetime, date
from io import BytesIO

import pandas as pd

from .models import db, Team, Player, Coach, AssessmentPeriod, Assessment


RAW_FIELDS = [
    "finding_space", "vision", "decision_making", "support_play",
    "reading_play", "reaction_to_losing_ball",
    "ball_control", "receiving_under_pressure", "twisting_turning",
    "one_v_one_dominance", "dribbling", "passing_range",
    "passing_quality", "attacking_heading", "crossing", "finishing",
    "hard_to_beat", "defensive_heading", "tackling", "interceptions",
    "competitive_edge", "bravery_on_ball", "bravery_without_ball",
    "control", "concentration", "communication",
    "tactical_potential", "technical_potential", "behavioural_potential",
]

OPTIONAL_FIELDS = ["coach_note"]


def _empty(value):
    return value is None or (isinstance(value, float) and pd.isna(value)) or str(value).strip() == ""


def _text(value):
    return "" if _empty(value) else str(value).strip()


def _int(value):
    if _empty(value):
        return None
    return int(float(value))


def _float(value):
    if _empty(value):
        raise ValueError("Hiányzó pontszám.")
    value = float(value)
    if not 1 <= value <= 10:
        raise ValueError("Minden értékelésnek 1 és 10 között kell lennie.")
    return value


def _date(value):
    if _empty(value):
        return None
    if isinstance(value, (datetime, date)):
        return value.date() if isinstance(value, datetime) else value
    return pd.to_datetime(value).date()


def _datetime(value):
    if _empty(value):
        return datetime.utcnow()
    parsed = pd.to_datetime(value)
    return parsed.to_pydatetime() if hasattr(parsed, "to_pydatetime") else parsed


def _find_by_id(model, value):
    value = _int(value)
    return db.session.get(model, value) if value else None


def _find_team(row):
    obj = _find_by_id(Team, row.get("team_id"))
    if obj:
        return obj
    name = _text(row.get("team_name"))
    return Team.query.filter_by(name=name).first() if name else None


def _find_coach(row):
    obj = _find_by_id(Coach, row.get("coach_id"))
    if obj:
        return obj
    name = _text(row.get("coach_name"))
    return Coach.query.filter_by(name=name).first() if name else None


def _find_period(row):
    obj = _find_by_id(AssessmentPeriod, row.get("period_id"))
    if obj:
        return obj
    name = _text(row.get("period_name"))
    return AssessmentPeriod.query.filter_by(name=name).first() if name else None


def _find_player(row):
    obj = _find_by_id(Player, row.get("player_id"))
    if obj:
        return obj

    code = _text(row.get("player_code"))
    if code:
        query = Player.query.filter_by(player_code=code)
        team = _find_team(row)
        if team:
            query = query.filter_by(team_id=team.id)
        obj = query.first()
        if obj:
            return obj

    first = _text(row.get("first_name"))
    last = _text(row.get("last_name"))
    if first and last:
        return Player.query.filter_by(first_name=first, last_name=last).first()

    return None


def _get_or_create_master(row, model):
    if model is Team:
        obj = _find_team(row)
        if not obj and _text(row.get("team_name")):
            obj = Team(name=_text(row["team_name"]))
            db.session.add(obj)
        return obj

    if model is Coach:
        obj = _find_coach(row)
        if not obj and _text(row.get("coach_name")):
            obj = Coach(name=_text(row["coach_name"]), email=_text(row.get("email")) or None)
            db.session.add(obj)
        return obj

    if model is AssessmentPeriod:
        obj = _find_period(row)
        if not obj and _text(row.get("period_name")):
            obj = AssessmentPeriod(
                name=_text(row["period_name"]),
                start_date=_date(row.get("start_date")),
                end_date=_date(row.get("end_date")),
            )
            db.session.add(obj)
        return obj


def import_backup_excel(file_storage):
    """Import a backup workbook. Existing records are skipped where possible."""
    content = file_storage.read()
    sheets = pd.read_excel(BytesIO(content), sheet_name=None)

    # Master data first.
    for sheet_name, model in [
        ("Teams", Team),
        ("Coaches", Coach),
        ("Assessment_Periods", AssessmentPeriod),
    ]:
        df = sheets.get(sheet_name)
        if df is not None:
            for _, raw in df.iterrows():
                row = raw.to_dict()
                if model is Team:
                    name = _text(row.get("name"))
                    if name and not Team.query.filter_by(name=name).first():
                        db.session.add(Team(name=name))
                elif model is Coach:
                    name = _text(row.get("name"))
                    if name and not Coach.query.filter_by(name=name).first():
                        db.session.add(Coach(name=name, email=_text(row.get("email")) or None))
                else:
                    name = _text(row.get("name"))
                    if name and not AssessmentPeriod.query.filter_by(name=name).first():
                        db.session.add(AssessmentPeriod(
                            name=name,
                            start_date=_date(row.get("start_date")),
                            end_date=_date(row.get("end_date")),
                        ))
            db.session.flush()

    # Players.
    players_df = sheets.get("Players")
    if players_df is not None:
        for _, raw in players_df.iterrows():
            row = raw.to_dict()
            existing = _find_player(row)
            if existing:
                continue

            team = _find_team(row)
            first = _text(row.get("first_name"))
            last = _text(row.get("last_name"))
            if not first or not last:
                raise ValueError("A játékos vezeték- és keresztneve kötelező.")

            player = Player(
                id=_int(row.get("id")) if _int(row.get("id")) and not db.session.get(Player, _int(row.get("id"))) else None,
                player_code=_text(row.get("player_code")) or None,
                first_name=first,
                last_name=last,
                birth_date=_date(row.get("birth_date")),
                active=bool(row.get("active", True)),
                team=team,
            )
            db.session.add(player)
        db.session.flush()

    # Assessments.
    assessments_df = sheets.get("Assessments")
    imported = 0
    skipped = 0

    if assessments_df is not None:
        for _, raw in assessments_df.iterrows():
            row = raw.to_dict()
            assessment_id = _int(row.get("assessment_id"))
            if assessment_id and db.session.get(Assessment, assessment_id):
                skipped += 1
                continue

            player = _find_player(row)
            team = _find_team(row)
            coach = _find_coach(row)
            period = _find_period(row)

            if not player or not team or not coach or not period:
                raise ValueError(
                    f"Hiányzó kapcsolat az értékelésnél: "
                    f"player={row.get('player_id')}, team={row.get('team_id')}, "
                    f"coach={row.get('coach_id')}, period={row.get('period_id')}"
                )

            if player.team_id != team.id:
                raise ValueError(
                    f"A játékos és a csapat nem egyezik: {player.full_name}"
                )

            duplicate = Assessment.query.filter_by(
                player_id=player.id,
                coach_id=coach.id,
                period_id=period.id,
            ).first()
            if duplicate:
                skipped += 1
                continue

            values = {field: _float(row.get(field)) for field in RAW_FIELDS}
            assessment = Assessment(
                player=player,
                team=team,
                coach=coach,
                period=period,
                completed_at=_datetime(row.get("completed_at")),
                coach_note=_text(row.get("coach_note")) or None,
                **values,
            )
            db.session.add(assessment)
            imported += 1

    db.session.commit()
    return {"imported": imported, "skipped": skipped}
