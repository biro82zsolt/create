
from sqlalchemy import inspect

from .models import db, Assessment


def migrate_assessment_potential_columns():
    """Add missing Potential columns without deleting existing data."""
    table_name = Assessment.__tablename__
    inspector = inspect(db.engine)

    if not inspector.has_table(table_name):
        return

    existing = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }

    potential_columns = [
        column
        for column in Assessment.__table__.columns
        if column.name.startswith("potential_")
    ]

    with db.engine.begin() as connection:
        for column in potential_columns:
            if column.name in existing:
                continue

            connection.exec_driver_sql(
                f'ALTER TABLE "{table_name}" '
                f'ADD COLUMN "{column.name}" FLOAT'
            )
            print(
                f"Added database column: "
                f"{table_name}.{column.name}"
            )
            existing.add(column.name)
