"""add rental days

Revision ID: 1e83306de3a1
Revises: 6ff122cecb82
Create Date: 2026-06-26 06:47:47.226378
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1e83306de3a1"
down_revision: Union[str, Sequence[str], None] = "6ff122cecb82"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add rental_days with a default so existing rows don't fail
    op.add_column(
        "book_requests",
        sa.Column(
            "rental_days",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    # Remove the default for future inserts
    op.alter_column(
        "book_requests",
        "rental_days",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("book_requests", "rental_days")
