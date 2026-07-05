import subprocess

from sqlalchemy import inspect, text

from app.database import Base, engine


def initialize_database():
    """
    Ensure tables exist and schema migrations are applied.

    Fresh databases are created from SQLAlchemy models.
    Existing databases run Alembic migrations incrementally.
    """
    inspector = inspect(engine)

    if not inspector.has_table("users"):
        Base.metadata.create_all(bind=engine)
        subprocess.run(
            ["alembic", "stamp", "head"],
            check=False,
            capture_output=True,
            text=True,
        )
        return

    subprocess.run(
        ["alembic", "upgrade", "head"],
        check=False,
        capture_output=True,
        text=True,
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE issued_books
                ADD COLUMN IF NOT EXISTS deposit_paid BOOLEAN NOT NULL DEFAULT false
                """
            )
        )
