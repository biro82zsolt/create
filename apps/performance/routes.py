# apps/performance/routes.py

from sqlalchemy import or_
from datetime import date

import pandas as pd

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
)

from .services import (
    analyze_assessment,
    aggregate_assessments,
    calculate_team_averages,
    calculate_age_group_averages,
    generate_player_pdf,
    calculate_player_insights,
)
from .models import (
    db,
    Team,
    Player,
    Coach,
    AssessmentPeriod,
    Assessment,
)

from .scoring import (
    get_questions_by_category,
    validate_assessment,
)

from .mapping import get_mapping_grid
from .constants import PERFORMANCE_ATTRIBUTES
from io import BytesIO
from datetime import datetime
from .auth import is_admin
from .import_service import import_backup_excel
from collections import defaultdict

performance_bp = Blueprint(
    "performance",
    __name__,
)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@performance_bp.get("/")
def dashboard():
    teams = Team.query.order_by(Team.name).all()

    return render_template(
        "performance/dashboard.html",
        teams=teams,
    )

@performance_bp.get("/guide")
def guide():
    return render_template(
        "performance/performance_guide.html"
    )

# ---------------------------------------------------------
# TEAMS
# ---------------------------------------------------------

@performance_bp.get("/teams")
def teams():
    teams = Team.query.order_by(Team.name).all()

    return render_template(
        "performance/teams.html",
        teams=teams,
    )


@performance_bp.post("/teams/create")
def create_team():
    name = request.form.get("name", "").strip()

    if not name:
        flash(
            "A csapat neve kötelező.",
            "error",
        )

        return redirect(
            url_for("performance.teams")
        )

    existing_team = Team.query.filter_by(
        name=name
    ).first()

    if existing_team:
        flash(
            "Ez a csapat már létezik.",
            "error",
        )

        return redirect(
            url_for("performance.teams")
        )

    team = Team(name=name)

    db.session.add(team)
    db.session.commit()

    flash(
        f"A(z) „{name}” csapat létrejött.",
        "success",
    )

    return redirect(
        url_for("performance.teams")
    )


# ---------------------------------------------------------
# TEAM PLAYERS
# ---------------------------------------------------------
@performance_bp.route("/teams/<int:team_id>", methods=["GET", "POST"])
def team_detail(team_id):

    team = db.session.get(Team, team_id)

    if not team:
        return "Team not found", 404

    if request.method == "POST":

        player_id = request.form.get("player_id", type=int)

        player = db.session.get(Player, player_id)

        if player and player not in team.roster_players:
            team.roster_players.append(player)
            db.session.commit()

        return redirect(
            url_for(
                "performance.team_detail",
                team_id=team.id,
            )
        )

    roster_player_ids = {
        player.id
        for player in team.roster_players
    }

    all_active_players = (
        Player.query
        .filter(Player.active.is_(True))
        .order_by(
            Player.last_name,
            Player.first_name,
        )
        .all()
    )

    players = [
        player
        for player in all_active_players
        if player.id not in roster_player_ids
    ]

    roster_players = sorted(
        team.roster_players,
        key=lambda player: (
            player.last_name,
            player.first_name,
        ),
    )

    return render_template(
        "performance/team_detail.html",
        team=team,
        players=players,
        roster_players=roster_players,
    )

@performance_bp.post("/teams/<int:team_id>/remove-player/<int:player_id>")
def remove_player_from_team(team_id, player_id):

    team = db.session.get(Team, team_id)
    player = db.session.get(Player, player_id)

    if not team or not player:
        return "Team or player not found", 404

    if player in team.roster_players:
        team.roster_players.remove(player)
        db.session.commit()

    return redirect(
        url_for(
            "performance.team_detail",
            team_id=team.id,
        )
    )

# ---------------------------------------------------------
# ALL PLAYERS
# ---------------------------------------------------------

@performance_bp.get("/players")
def players():

    search = request.args.get(
        "search",
        "",
    ).strip()

    birth_year = request.args.get(
        "birth_year",
        type=int,
    )

    team_id = request.args.get(
        "team_id",
        type=int,
    )

    query = Player.query.filter(
        Player.active.is_(True)
    )

    # Keresés név vagy játékoskód alapján
    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                Player.first_name.ilike(search_pattern),
                Player.last_name.ilike(search_pattern),
                Player.player_code.ilike(search_pattern),
            )
        )

    # Születési év szerinti szűrés
    if birth_year:

        query = query.filter(
            db.extract(
                "year",
                Player.birth_date,
            ) == birth_year
        )

    # Csapat szerinti szűrés
    if team_id:

        query = query.filter(
            Player.team_id == team_id
        )

    players = query.order_by(
        Player.last_name,
        Player.first_name,
    ).all()

    teams = Team.query.order_by(
        Team.name
    ).all()

    return render_template(
        "performance/players.html",
        players=players,
        teams=teams,
        search=search,
        birth_year=birth_year,
        selected_team_id=team_id,
    )

# ---------------------------------------------------------
# PLAYER DETAIL
# ---------------------------------------------------------

@performance_bp.get("/players/<int:player_id>")
def player_detail(player_id):
    player = db.session.get(Player, player_id)

    if not player:
        return "Player not found", 404

    view = request.args.get("view", "current")

    period_id = request.args.get(
        "period_id",
        type=int,
    )

    selected_period_ids = request.args.get(
        "period_ids",
        "",
    )

    context = get_player_detail_context(
        player=player,
        view=view,
        period_id=period_id,
        selected_period_ids=selected_period_ids,
    )

    return render_template(
        "performance/player_detail.html",
        **context
    )

def build_period_results(assessments, limit=None):
    """
    A játékos értékeléseit mérési időszakonként csoportosítja,
    majd minden időszakhoz külön aggregált eredményt készít.
    """

    grouped = defaultdict(list)
    periods = {}

    for assessment in assessments:

        if not assessment.period_id or not assessment.period:
            continue

        grouped[assessment.period_id].append(assessment)
        periods[assessment.period_id] = assessment.period

    period_results = []

    for period_id, period_assessments in grouped.items():

        result = aggregate_assessments(period_assessments)

        if result is None:
            continue

        period = periods[period_id]

        period_results.append({
            "period": period,
            "period_id": period.id,
            "result": result,
            "assessment_count": len(period_assessments),
        })

    period_results.sort(
        key=lambda item: (
            item["period"].start_date or date.min,
            item["period_id"],
        ),
        reverse=True,
    )

    if limit:
        return period_results[:limit]

    return period_results

def get_player_detail_context(
    player,
    view="current",
    period_id=None,
    selected_period_ids="",
):

    assessments = (
        Assessment.query
        .filter_by(player_id=player.id)
        .order_by(Assessment.completed_at.desc())
        .all()
    )

    # -----------------------------------------------------
    # PERIOD RESULTS
    # -----------------------------------------------------

    period_results = build_period_results(assessments)

    # -----------------------------------------------------
    # CURRENT PERIOD
    # -----------------------------------------------------

    current_item = None

    if period_id is not None:

        current_item = next(
            (
                item
                for item in period_results
                if item["period_id"] == period_id
            ),
            None,
        )

    if current_item is None:

        active_items = [
            item
            for item in period_results
            if is_period_active(item["period"])
        ]

        if active_items:
            current_item = active_items[0]

        elif period_results:
            current_item = period_results[0]

    current_period = (
        current_item["period"]
        if current_item
        else None
    )

    aggregated_result = (
        current_item["result"]
        if current_item
        else None
    )

    # -----------------------------------------------------
    # CURRENT ASSESSMENTS
    # -----------------------------------------------------

    current_assessments = []

    if current_period:

        current_assessments = [
            assessment
            for assessment in assessments
            if assessment.period_id == current_period.id
        ]

    assessment_results = []

    for assessment in current_assessments:

        result = analyze_assessment(assessment)

        assessment_results.append({
            "assessment": assessment,
            "result": result,
        })

    # -----------------------------------------------------
    # TREND PERIODS
    # -----------------------------------------------------

    if selected_period_ids:

        try:
            selected_ids = [
                int(value.strip())
                for value in selected_period_ids.split(",")
                if value.strip()
            ]
        except ValueError:
            selected_ids = []

        trend_results = [
            item
            for item in period_results
            if item["period_id"] in selected_ids
        ]

        trend_results.sort(
            key=lambda item: (
                item["period"].start_date or date.min,
                item["period_id"],
            )
        )

    else:

        # Alapértelmezés: 4 legutóbbi időszak
        trend_results = period_results[:4]

        trend_results.reverse()

    # -----------------------------------------------------
    # AGE GROUP AVERAGES
    # -----------------------------------------------------

    age_group_averages = None

    if current_period and player.birth_date:

        age_group_averages = calculate_age_group_averages(
            birth_year=player.birth_date.year,
            period_id=current_period.id,
        )

    # -----------------------------------------------------
    # INSIGHTS
    # -----------------------------------------------------

    insights = None

    if aggregated_result and age_group_averages:

        insights = calculate_player_insights(
            player_attributes=aggregated_result["attributes"],
            team_attributes=age_group_averages["attributes"],
        )

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    return {
        "player": player,

        "view": view,

        "current_period": current_period,

        "available_periods": period_results,

        "assessments": assessment_results,

        # Az aktuális adatlap továbbra is ezt használja
        "aggregated": aggregated_result,

        "team_averages": age_group_averages,

        "mapping_grid": get_mapping_grid(),

        "insights": insights,

        "performance_attributes": PERFORMANCE_ATTRIBUTES,

        # A trendnézet számára
        "trend_results": trend_results,
    }

# ---------------------------------------------------------
# EXCEL IMPORT PREVIEW
# ---------------------------------------------------------

@performance_bp.post(
    "/teams/<int:team_id>/players/import-preview"
)
def import_players_preview(team_id):

    team = db.session.get(
        Team,
        team_id,
    )

    if not team:
        return "Team not found", 404

    file = request.files.get("file")

    if not file or file.filename == "":
        flash(
            "Válassz ki egy Excel fájlt.",
            "error",
        )

        return redirect(
            url_for(
                "performance.team_detail",
                team_id=team.id,
            )
        )

    try:
        df = pd.read_excel(file)

    except Exception as exc:
        flash(
            f"Az Excel fájl nem olvasható: {exc}",
            "error",
        )

        return redirect(
            url_for(
                "performance.team_detail",
                team_id=team.id,
            )
        )

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = [
        "Last Name",
        "First Name",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        flash(
            "Hiányzó oszlop(ok): "
            + ", ".join(missing_columns),
            "error",
        )

        return redirect(
            url_for(
                "performance.team_detail",
                team_id=team.id,
            )
        )

    # -----------------------------------------------------
    # BUILD PREVIEW
    # -----------------------------------------------------

    preview = []

    # Ezeket MINDEN új Excel importnál
    # nulláról indítjuk.
    seen_player_codes = set()
    seen_names = set()

    for index, row in df.iterrows():

        row_number = index + 2

        last_name = str(
            row.get("Last Name", "")
        ).strip()

        first_name = str(
            row.get("First Name", "")
        ).strip()

        if last_name == "nan":
            last_name = ""

        if first_name == "nan":
            first_name = ""

        # -------------------------------------------------
        # PLAYER ID
        # -------------------------------------------------

        player_code = row.get("Player ID")

        if pd.isna(player_code):

            player_code = None

        else:

            # Excelből gyakran 1001.0 érkezik.
            # Ezt 1001-ként kezeljük.
            if (
                isinstance(player_code, float)
                and player_code.is_integer()
            ):

                player_code = str(
                    int(player_code)
                )

            else:

                player_code = str(
                    player_code
                ).strip()

        # -------------------------------------------------
        # BIRTH DATE
        # -------------------------------------------------

        birth_date = row.get(
            "Birth Date"
        )

        if pd.isna(birth_date):

            birth_date = None

        else:

            try:

                birth_date = pd.to_datetime(
                    birth_date
                ).date()

            except Exception:

                birth_date = None

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        status = "new"
        status_text = "Új játékos"

        # -------------------------------------------------
        # REQUIRED NAME VALIDATION
        # -------------------------------------------------

        if not last_name or not first_name:

            status = "error"
            status_text = "Hiányzó név"

        else:

            existing_player = None

            # -------------------------------------------------
            # CHECK DATABASE BY PLAYER ID
            # -------------------------------------------------

            if player_code:

                existing_player = (
                    Player.query
                    .filter_by(
                        team_id=team.id,
                        player_code=player_code,
                    )
                    .first()
                )

            # -------------------------------------------------
            # CHECK DATABASE BY NAME
            # -------------------------------------------------

            if not existing_player:

                existing_player = (
                    Player.query
                    .filter_by(
                        team_id=team.id,
                        last_name=last_name,
                        first_name=first_name,
                    )
                    .first()
                )

            if existing_player:

                status = "existing"
                status_text = "Már létezik"

            else:

                # -------------------------------------------------
                # CHECK DUPLICATE INSIDE EXCEL
                # -------------------------------------------------

                duplicate_in_excel = False

                if player_code:

                    if player_code in seen_player_codes:
                        duplicate_in_excel = True

                name_key = (
                    last_name.lower(),
                    first_name.lower(),
                )

                if name_key in seen_names:
                    duplicate_in_excel = True

                if duplicate_in_excel:

                    status = "duplicate"
                    status_text = "Duplikált az Excelben"

                else:

                    if player_code:
                        seen_player_codes.add(
                            player_code
                        )

                    seen_names.add(
                        name_key
                    )

        # -------------------------------------------------
        # ADD TO PREVIEW
        # -------------------------------------------------

        preview.append({
            "row": row_number,
            "player_code": player_code,
            "last_name": last_name,
            "first_name": first_name,
            "birth_date": birth_date,
            "status": status,
            "status_text": status_text,
        })

    # ---------------------------------------------------------
    # STORE PREVIEW IN SESSION
    # ---------------------------------------------------------

    session["player_import_preview"] = [
        {
            **item,
            "birth_date": (
                item["birth_date"].isoformat()
                if item["birth_date"]
                else None
            ),
        }
        for item in preview
    ]

    session["player_import_team_id"] = team.id

    return render_template(
        "performance/player_import_preview.html",
        team=team,
        preview=preview,
    )


# ---------------------------------------------------------
# CONFIRM EXCEL IMPORT
# ---------------------------------------------------------

@performance_bp.post(
    "/teams/<int:team_id>/players/import-confirm"
)
def import_players_confirm(team_id):

    team = db.session.get(
        Team,
        team_id,
    )

    if not team:
        return "Team not found", 404

    preview = session.get(
        "player_import_preview"
    )

    preview_team_id = session.get(
        "player_import_team_id"
    )

    if (
        not preview
        or preview_team_id != team.id
    ):

        flash(
            "Nincs megerősíthető import.",
            "error",
        )

        return redirect(
            url_for(
                "performance.team_detail",
                team_id=team.id,
            )
        )

    created = 0

    for item in preview:

        # Csak a ténylegesen új játékosokat
        # importáljuk.
        if item["status"] != "new":
            continue

        player = Player(
            team_id=team.id,
            player_code=item["player_code"],
            first_name=item["first_name"],
            last_name=item["last_name"],
        )

        if item["birth_date"]:

            player.birth_date = date.fromisoformat(
                item["birth_date"]
            )

        db.session.add(player)

        created += 1

    # -----------------------------------------------------
    # DATABASE COMMIT
    # -----------------------------------------------------

    try:

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        return {
            "status": "error",
            "error": str(exc),
        }, 500

    # -----------------------------------------------------
    # CLEAR SESSION
    # -----------------------------------------------------

    session.pop(
        "player_import_preview",
        None,
    )

    session.pop(
        "player_import_team_id",
        None,
    )

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    flash(
        f"{created} új játékos importálva.",
        "success",
    )

    return redirect(
        url_for(
            "performance.team_detail",
            team_id=team.id,
        )
    )

@performance_bp.get("/assessment/new")
def assessment_new():
    teams = (
        Team.query
        .order_by(Team.name)
        .all()
    )

    players = (
        Player.query
        .filter(Player.active.is_(True))
        .order_by(
            Player.last_name,
            Player.first_name,
        )
        .all()
    )

    coaches = (
        Coach.query
        .order_by(Coach.name)
        .all()
    )

    today = date.today()

    periods = (
        AssessmentPeriod.query
        .filter(
            AssessmentPeriod.start_date.isnot(None),
            AssessmentPeriod.end_date.isnot(None),
            AssessmentPeriod.start_date <= today,
            AssessmentPeriod.end_date >= today,
        )
        .order_by(AssessmentPeriod.name.desc())
        .all()
    )

    return render_template(
        "performance/assessment_start.html",
        teams=teams,
        players=players,
        coaches=coaches,
        periods=periods,
    )

def is_period_active(period):
    today = date.today()

    return (
        period is not None
        and period.start_date is not None
        and period.end_date is not None
        and period.start_date <= today <= period.end_date
    )

@performance_bp.post("/assessment/start")
def assessment_start():

    team_id = request.form.get("team_id", type=int)
    player_id = request.form.get("player_id", type=int)
    coach_id = request.form.get("coach_id", type=int)
    period_id = request.form.get("period_id", type=int)

    team = db.session.get(Team, team_id) if team_id else None
    player = db.session.get(Player, player_id)
    coach = db.session.get(Coach, coach_id)
    period = db.session.get(AssessmentPeriod, period_id)

    if not is_period_active(period):
        flash(
            "Ez az értékelési időszak jelenleg nem aktív.",
            "error",
        )

        return redirect(
            url_for("performance.assessment_new")
        )

    if not all([player, coach, period]):
        flash(
            "A játékos, az edző és az időszak megadása kötelező.",
            "error",
        )

        return redirect(
            url_for("performance.assessment_new")
        )

    return render_template(
        "performance/assessment_form.html",
        team=team,
        player=player,
        coach=coach,
        period=period,
        tactical=get_questions_by_category("tactical"),
        technical=get_questions_by_category("technical"),
        behaviour=get_questions_by_category("behaviour"),
        potential=get_questions_by_category("potential"),
    )

@performance_bp.post("/assessment/save")
def assessment_save():
    team_id = request.form.get("team_id", type=int)
    player_id = request.form.get("player_id", type=int)
    coach_id = request.form.get("coach_id", type=int)
    period_id = request.form.get("period_id", type=int)

    team = db.session.get(Team, team_id) if team_id else None
    player = db.session.get(Player, player_id)
    coach = db.session.get(Coach, coach_id)
    period = db.session.get(AssessmentPeriod, period_id)

    if not is_period_active(period):
        flash(
            "Ez az értékelési időszak jelenleg nem aktív.",
            "error",
        )

        return redirect(
            url_for("performance.assessment_new")
        )

    if not all([player, coach, period]):
        flash(
            "A játékos, az edző és az időszak megadása kötelező.",
            "error",
        )

        return redirect(
            url_for("performance.assessment_new")
        )

    # -----------------------------------------------------
    # READ RATINGS
    # -----------------------------------------------------

    scores = {}

    for question in (
        get_questions_by_category("tactical")
        + get_questions_by_category("technical")
        + get_questions_by_category("behaviour")
        + get_questions_by_category("potential")
    ):
        code = question["code"]
        value = request.form.get(code)

        if value is None or value == "":
            flash(
                f"Hiányzó értékelés: {question['name']}",
                "error",
            )
            return redirect(
                url_for("performance.assessment_new")
            )

        scores[code] = value

    # -----------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------

    try:
        validate_assessment(scores)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(
            url_for("performance.assessment_new")
        )

    # -----------------------------------------------------
    # CHECK DUPLICATE
    # -----------------------------------------------------

    existing = Assessment.query.filter_by(
        player_id=player.id,
        coach_id=coach.id,
        period_id=period.id,
    ).first()

    if existing:
        flash(
            "Ez az edző ebben az időszakban már értékelte ezt a játékost.",
            "error",
        )
        return redirect(
            url_for(
                "performance.player_detail",
                player_id=player.id,
            )
        )

    # -----------------------------------------------------
    # CREATE ASSESSMENT
    # -----------------------------------------------------

    assessment = Assessment(
        team_id=team.id if team else None,
        player_id=player.id,
        coach_id=coach.id,
        period_id=period.id,

        # Tactical
        finding_space=float(scores["finding_space"]),
        vision=float(scores["vision"]),
        decision_making=float(scores["decision_making"]),
        support_play=float(scores["support_play"]),
        reading_play=float(scores["reading_play"]),
        reaction_to_losing_ball=float(
            scores["reaction_to_losing_ball"]
        ),

        # Technical
        ball_control=float(scores["ball_control"]),
        receiving_under_pressure=float(
            scores["receiving_under_pressure"]
        ),
        twisting_turning=float(
            scores["twisting_turning"]
        ),
        one_v_one_dominance=float(
            scores["one_v_one_dominance"]
        ),
        dribbling=float(scores["dribbling"]),
        passing_range=float(scores["passing_range"]),
        passing_quality=float(scores["passing_quality"]),
        attacking_heading=float(
            scores["attacking_heading"]
        ),
        crossing=float(scores["crossing"]),
        finishing=float(scores["finishing"]),
        hard_to_beat=float(scores["hard_to_beat"]),
        defensive_heading=float(
            scores["defensive_heading"]
        ),
        tackling=float(scores["tackling"]),
        interceptions=float(scores["interceptions"]),

        # Behaviour
        competitive_edge=float(
            scores["competitive_edge"]
        ),
        bravery_on_ball=float(
            scores["bravery_on_ball"]
        ),
        bravery_without_ball=float(
            scores["bravery_without_ball"]
        ),
        control=float(scores["control"]),
        concentration=float(
            scores["concentration"]
        ),
        communication=float(
            scores["communication"]
        ),

        # Potential
        tactical_potential=float(
            scores["tactical_potential"]
        ),
        technical_potential=float(
            scores["technical_potential"]
        ),
        behavioural_potential=float(
            scores["behavioural_potential"]
        ),

        coach_note=request.form.get(
            "coach_note",
            ""
        ).strip(),
    )

    db.session.add(assessment)
    db.session.commit()

    flash(
        "Az értékelés sikeresen mentve.",
        "success",
    )

    return redirect(
        url_for(
            "performance.player_detail",
            player_id=player.id,
        )
    )

# ---------------------------------------------------------
# ASSESSMENTS ADMINISTRATION
# ---------------------------------------------------------

@performance_bp.get("/assessments")
def assessments():

    player_id = request.args.get(
        "player_id",
        type=int,
    )

    team_id = request.args.get(
        "team_id",
        type=int,
    )

    coach_id = request.args.get(
        "coach_id",
        type=int,
    )

    period_id = request.args.get(
        "period_id",
        type=int,
    )

    query = Assessment.query

    if player_id:
        query = query.filter(
            Assessment.player_id == player_id
        )

    if team_id:
        query = query.filter(
            Assessment.team_id == team_id
        )

    if coach_id:
        query = query.filter(
            Assessment.coach_id == coach_id
        )

    if period_id:
        query = query.filter(
            Assessment.period_id == period_id
        )

    assessments = (
        query
        .order_by(
            Assessment.completed_at.desc()
        )
        .all()
    )

    players = (
        Player.query
        .filter(Player.active.is_(True))
        .order_by(
            Player.last_name,
            Player.first_name,
        )
        .all()
    )

    teams = Team.query.order_by(
        Team.name
    ).all()

    coaches = Coach.query.order_by(
        Coach.name
    ).all()

    periods = AssessmentPeriod.query.order_by(
        AssessmentPeriod.name.desc()
    ).all()

    return render_template(
        "performance/assessments.html",
        assessments=assessments,
        players=players,
        teams=teams,
        coaches=coaches,
        periods=periods,
        selected_player_id=player_id,
        selected_team_id=team_id,
        selected_coach_id=coach_id,
        selected_period_id=period_id,
    )

# ---------------------------------------------------------
# DUPLICATE PLAYER CHECK
# ---------------------------------------------------------

@performance_bp.get("/duplicates")
def duplicate_players():

    from collections import defaultdict

    players = (
        Player.query
        .order_by(
            Player.last_name,
            Player.first_name,
            Player.id,
        )
        .all()
    )

    grouped_players = defaultdict(list)

    for player in players:

        name_key = (
            player.last_name.strip().lower(),
            player.first_name.strip().lower(),
        )

        if player.last_name and player.first_name:
            grouped_players[name_key].append(player)

    duplicate_groups = [
        group
        for group in grouped_players.values()
        if len(group) > 1
    ]

    return render_template(
        "performance/duplicates.html",
        duplicate_groups=duplicate_groups,
    )

# ---------------------------------------------------------
# DUPLICATE PLAYER COMPARISON
# ---------------------------------------------------------

@performance_bp.get("/duplicates/compare")
def compare_duplicate_players():

    player_a_id = request.args.get(
        "player_a_id",
        type=int,
    )

    player_b_id = request.args.get(
        "player_b_id",
        type=int,
    )

    player_a = db.session.get(Player, player_a_id)
    player_b = db.session.get(Player, player_b_id)

    if not player_a or not player_b:
        return "Player not found", 404

    if (
        player_a.last_name.strip().lower()
        != player_b.last_name.strip().lower()
        or
        player_a.first_name.strip().lower()
        != player_b.first_name.strip().lower()
    ):
        flash(
            "Csak azonos nevű játékosok hasonlíthatók össze.",
            "error",
        )

        return redirect(
            url_for("performance.duplicate_players")
        )

    return render_template(
        "performance/duplicate_compare.html",
        player_a=player_a,
        player_b=player_b,
    )

# ---------------------------------------------------------
# MERGE PREVIEW
# ---------------------------------------------------------

# ---------------------------------------------------------
# MERGE PREVIEW
# ---------------------------------------------------------

@performance_bp.get("/duplicates/merge-preview")
def merge_duplicate_preview():

    keep_id = request.args.get("keep_id", type=int)
    merge_id = request.args.get("merge_id", type=int)

    keep_player = db.session.get(Player, keep_id)
    merge_player = db.session.get(Player, merge_id)

    if not keep_player or not merge_player:
        return "Player not found", 404

    if keep_player.id == merge_player.id:
        return "A két játékos nem lehet azonos.", 400

    keep_keys = {
        (a.coach_id, a.period_id)
        for a in keep_player.assessments
    }

    move_assessments = []
    conflict_assessments = []

    for assessment in merge_player.assessments:

        key = (
            assessment.coach_id,
            assessment.period_id,
        )

        if key in keep_keys:
            conflict_assessments.append(assessment)
        else:
            move_assessments.append(assessment)

    return render_template(
        "performance/merge_preview.html",
        keep_player=keep_player,
        merge_player=merge_player,
        move_assessments=move_assessments,
        conflict_assessments=conflict_assessments,
    )

# ---------------------------------------------------------
# MERGE PLAYERS
# ---------------------------------------------------------

@performance_bp.post("/duplicates/merge")
def merge_duplicate_players():

    keep_id = request.form.get("keep_id", type=int)
    merge_id = request.form.get("merge_id", type=int)

    keep_player = db.session.get(Player, keep_id)
    merge_player = db.session.get(Player, merge_id)

    if not keep_player or not merge_player:
        flash(
            "A játékosrekord nem található.",
            "error",
        )

        return redirect(
            url_for("performance.duplicate_players")
        )

    if keep_player.id == merge_player.id:
        flash(
            "A két rekord nem lehet azonos.",
            "error",
        )

        return redirect(
            url_for("performance.duplicate_players")
        )

    try:

        # -------------------------------------------------
        # EXISTING ASSESSMENTS OF THE KEEP PLAYER
        # -------------------------------------------------

        keep_assessments = {
            (assessment.coach_id, assessment.period_id)
            for assessment in keep_player.assessments
        }

        # -------------------------------------------------
        # MERGE ASSESSMENTS
        # -------------------------------------------------

        deleted_conflicts = 0
        moved_assessments = 0

        for assessment in list(merge_player.assessments):

            assessment_key = (
                assessment.coach_id,
                assessment.period_id,
            )

            if assessment_key in keep_assessments:

                # Ütközés esetén a megtartott rekord
                # értékelése marad meg.
                db.session.delete(assessment)

                deleted_conflicts += 1

            else:

                # Ütközésmentes értékelés áthelyezése.
                assessment.player_id = keep_player.id

                moved_assessments += 1

        # -------------------------------------------------
        # MERGE ROSTER RELATIONSHIPS
        # -------------------------------------------------

        for team in list(merge_player.roster_teams):

            if team not in keep_player.roster_teams:

                keep_player.roster_teams.append(team)

        # -------------------------------------------------
        # DEACTIVATE DUPLICATE
        # -------------------------------------------------

        merge_player.active = False

        db.session.flush()
        db.session.commit()

        flash(
            f"Az összevonás sikeres. "
            f"Áthelyezett értékelések: {moved_assessments}. "
            f"Ütközés miatt törölt értékelések: "
            f"{deleted_conflicts}. "
            f"A megtartott rekord ID-ja: {keep_player.id}.",
            "success",
        )

    except Exception as exc:

        db.session.rollback()

        flash(
            f"Az összevonás sikertelen: {exc}",
            "error",
        )

    return redirect(
        url_for(
            "performance.player_detail",
            player_id=keep_player.id,
        )
    )

@performance_bp.get("/players/<int:player_id>/pdf")
def player_pdf(player_id):
    player = db.session.get(Player, player_id)

    if not player:
        return "Player not found", 404

    context = get_player_detail_context(player)

    if not context["assessments"]:
        flash(
            "A játékoshoz még nem tartozik értékelés.",
            "warning"
        )
        return redirect(
            url_for(
                "performance.player_detail",
                player_id=player_id
            )
        )

    pdf_buffer = generate_player_pdf(
        player=context["player"],
        aggregated=context["aggregated"],
        team_averages=context["team_averages"],
        assessments=context["assessments"],
        insights=context["insights"],
    )

    filename = (
        f"{player.last_name}_{player.first_name}"
        "_performance_assessment.pdf"
    )

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )

# ---------------------------------------------------------
# EXCEL EXPORTS
# ---------------------------------------------------------

@performance_bp.get("/admin/export/assessments")
def export_assessments():

    from .exports import create_assessments_dataframe

    df = create_assessments_dataframe()

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Assessments",
            index=False,
        )

    output.seek(0)

    filename = (
        "performance_assessments_"
        f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    )

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


@performance_bp.get("/admin/export/backup")
def export_backup():

    from .exports import create_backup_excel

    output = create_backup_excel()

    filename = (
        "performance_backup_"
        f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    )

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )