"""Create organization table

Revision ID: bf3d800c00a2
Revises: 8ce1abeb55d0
Create Date: 2025-05-21 11:52:37.145925+00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "bf3d800c00a2"
down_revision = "8ce1abeb55d0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organization",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.Column(
            "name_fts",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('russian', name)", persisted=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["building_id"],
            ["building.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_organization_name_fts",
        "organization",
        ["name_fts"],
        unique=False,
        postgresql_using="gin",
    )

    op.create_index(
        "ix_organization_name_trgm",
        "organization",
        ["name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )

    op.create_table(
        "organization_activity",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activity.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("organization_id", "activity_id"),
    )


def downgrade():
    op.drop_table("organization_activity")

    op.drop_index(
        "ix_organization_name_trgm",
        table_name="organization",
        postgresql_using="gin",
        postgresql_ops={"content": "gin_trgm_ops"},
    )

    op.drop_index(
        "ix_organization_name_fts",
        table_name="organization",
        postgresql_using="gin",
    )

    op.drop_table("organization")
