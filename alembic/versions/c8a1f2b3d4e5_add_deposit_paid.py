"""add deposit_paid to issued books

Revision ID: c8a1f2b3d4e5
Revises: d17a694bb426
Create Date: 2026-07-05 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c8a1f2b3d4e5"
down_revision: Union[str, Sequence[str], None] = "d17a694bb426"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "issued_books",
        sa.Column(
            "deposit_paid",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("issued_books", "deposit_paid")
