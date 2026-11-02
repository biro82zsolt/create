"""Reset the Performance app database for development/test use only.

WARNING: This permanently deletes all Performance app records.
Run from the monorepo root with the appropriate Python environment:
    python -m apps.performance.reset_test_database
Do not run against a database containing production data.
"""

from .app import app
from .models import db


def reset_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Performance test database reset; empty schema created.")


if __name__ == "__main__":
    confirmation = input(
        "This deletes ALL Performance app data. Type RESET to continue: "
    )
    if confirmation == "RESET":
        reset_database()
    else:
        print("Cancelled; database unchanged.")
