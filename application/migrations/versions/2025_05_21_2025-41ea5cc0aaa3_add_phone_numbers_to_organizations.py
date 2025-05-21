"""Add phone numbers to organizations

Revision ID: 41ea5cc0aaa3
Revises: bf3d800c00a2
Create Date: 2025-05-21 20:25:40.237121+00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "41ea5cc0aaa3"
down_revision = "bf3d800c00a2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "organization",
        sa.Column("phone_number", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("organization", "phone_number")
