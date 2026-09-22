"""Authentication helpers for the Performance application."""

import os
from pathlib import Path
from functools import wraps

from dotenv import load_dotenv

from flask import redirect, request, session, url_for, flash
from werkzeug.security import check_password_hash

# Helyi .env betöltése
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

COACH_USERNAME = os.environ.get(
    "COACH_USERNAME",
    "coach",
)

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "admin",
)

COACH_PASSWORD_HASH = os.environ.get(
    "COACH_PASSWORD_HASH",
    "",
)

ADMIN_PASSWORD_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH",
    "",
)


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

def login_coach(username, password):
    return (
        username == COACH_USERNAME
        and bool(COACH_PASSWORD_HASH)
        and check_password_hash(
            COACH_PASSWORD_HASH,
            password,
        )
    )


def login_admin(username, password):
    return (
        username == ADMIN_USERNAME
        and bool(ADMIN_PASSWORD_HASH)
        and check_password_hash(
            ADMIN_PASSWORD_HASH,
            password,
        )
    )


# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------

def is_authenticated():
    return session.get("auth_role") in {
        "coach",
        "admin",
    }


def is_admin():
    return session.get("auth_role") == "admin"


# ---------------------------------------------------------
# DECORATORS
# ---------------------------------------------------------

def coach_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_authenticated():
            return redirect(
                url_for(
                    "login",
                    next=request.path,
                )
            )

        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_admin():
            flash(
                "Admin jogosultság szükséges.",
                "error",
            )

            return redirect(
                url_for(
                    "admin_login",
                    next=request.path,
                )
            )

        return view(*args, **kwargs)

    return wrapped