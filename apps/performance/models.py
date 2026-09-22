# apps/performance/models.py

from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint


db = SQLAlchemy()

team_players = db.Table(
    "performance_team_players",

    db.Column(
        "team_id",
        db.Integer,
        db.ForeignKey("performance_teams.id"),
        primary_key=True,
    ),

    db.Column(
        "player_id",
        db.Integer,
        db.ForeignKey("performance_players.id"),
        primary_key=True,
    ),
)

class Team(db.Model):
    __tablename__ = "performance_teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    players = db.relationship(
        "Player",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    roster_players = db.relationship(
        "Player",
        secondary=team_players,
        back_populates="roster_teams",
    )

    assessments = db.relationship(
        "Assessment",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Team {self.name}>"


class Coach(db.Model):
    __tablename__ = "performance_coaches"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    assessments = db.relationship(
        "Assessment",
        back_populates="coach",
    )

    def __repr__(self):
        return f"<Coach {self.name}>"


class Player(db.Model):
    __tablename__ = "performance_players"

    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(
        db.Integer,
        db.ForeignKey("performance_teams.id"),
        nullable=True,
    )

    player_code = db.Column(db.String(50), nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)

    active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    team = db.relationship(
        "Team",
        back_populates="players",
    )

    roster_teams = db.relationship(
        "Team",
        secondary=team_players,
        back_populates="roster_players",
    )

    assessments = db.relationship(
        "Assessment",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "player_code",
            name="uq_performance_player_team_code",
        ),
    )

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __repr__(self):
        return f"<Player {self.full_name}>"


class AssessmentPeriod(db.Model):
    __tablename__ = "performance_assessment_periods"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    assessments = db.relationship(
        "Assessment",
        back_populates="period",
    )

    def __repr__(self):
        return f"<AssessmentPeriod {self.name}>"


class Assessment(db.Model):
    __tablename__ = "performance_assessments"

    id = db.Column(db.Integer, primary_key=True)

    # Kapcsolatok
    team_id = db.Column(
        db.Integer,
        db.ForeignKey("performance_teams.id"),
        nullable=True,
    )

    player_id = db.Column(
        db.Integer,
        db.ForeignKey("performance_players.id"),
        nullable=False,
    )

    coach_id = db.Column(
        db.Integer,
        db.ForeignKey("performance_coaches.id"),
        nullable=False,
    )

    period_id = db.Column(
        db.Integer,
        db.ForeignKey("performance_assessment_periods.id"),
        nullable=False,
    )

    completed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # ---------------------------------------------------------
    # PERFORMANCE – TACTICAL
    # ---------------------------------------------------------

    finding_space = db.Column(db.Float, nullable=False)
    vision = db.Column(db.Float, nullable=False)
    decision_making = db.Column(db.Float, nullable=False)
    support_play = db.Column(db.Float, nullable=False)
    reading_play = db.Column(db.Float, nullable=False)
    reaction_to_losing_ball = db.Column(db.Float, nullable=False)

    # ---------------------------------------------------------
    # PERFORMANCE – TECHNICAL
    # ---------------------------------------------------------

    ball_control = db.Column(db.Float, nullable=False)
    receiving_under_pressure = db.Column(db.Float, nullable=False)
    twisting_turning = db.Column(db.Float, nullable=False)
    one_v_one_dominance = db.Column(db.Float, nullable=False)
    dribbling = db.Column(db.Float, nullable=False)
    passing_range = db.Column(db.Float, nullable=False)
    passing_quality = db.Column(db.Float, nullable=False)
    attacking_heading = db.Column(db.Float, nullable=False)
    crossing = db.Column(db.Float, nullable=False)
    finishing = db.Column(db.Float, nullable=False)
    hard_to_beat = db.Column(db.Float, nullable=False)
    defensive_heading = db.Column(db.Float, nullable=False)
    tackling = db.Column(db.Float, nullable=False)
    interceptions = db.Column(db.Float, nullable=False)

    # ---------------------------------------------------------
    # PERFORMANCE – BEHAVIOUR
    # ---------------------------------------------------------

    competitive_edge = db.Column(db.Float, nullable=False)
    bravery_on_ball = db.Column(db.Float, nullable=False)
    bravery_without_ball = db.Column(db.Float, nullable=False)
    control = db.Column(db.Float, nullable=False)
    concentration = db.Column(db.Float, nullable=False)
    communication = db.Column(db.Float, nullable=False)

    # ---------------------------------------------------------
    # POTENTIAL
    # ---------------------------------------------------------

    tactical_potential = db.Column(db.Float, nullable=False)
    technical_potential = db.Column(db.Float, nullable=False)
    behavioural_potential = db.Column(db.Float, nullable=False)

    # ---------------------------------------------------------
    # EXTRA
    # ---------------------------------------------------------

    coach_note = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships

    team = db.relationship(
        "Team",
        back_populates="assessments",
    )

    player = db.relationship(
        "Player",
        back_populates="assessments",
    )

    coach = db.relationship(
        "Coach",
        back_populates="assessments",
    )

    period = db.relationship(
        "AssessmentPeriod",
        back_populates="assessments",
    )

    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "coach_id",
            "period_id",
            name="uq_performance_assessment",
        ),
    )

    def __repr__(self):
        return (
            f"<Assessment player={self.player_id} "
            f"coach={self.coach_id} "
            f"period={self.period_id}>"
        )