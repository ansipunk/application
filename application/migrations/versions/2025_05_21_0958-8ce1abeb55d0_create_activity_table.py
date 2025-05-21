"""Create activity table

Revision ID: 8ce1abeb55d0
Revises: 97690affcdf0
Create Date: 2025-05-21 09:58:28.565695+00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "8ce1abeb55d0"
down_revision = "97690affcdf0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column(
            "level",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["activity.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("activity")
