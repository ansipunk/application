"""Make phone numbers a one-to-many table

Revision ID: 600c14c93aca
Revises: 41ea5cc0aaa3
Create Date: 2025-05-25 15:06:52.854813+00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "600c14c93aca"
down_revision = "41ea5cc0aaa3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organization_phone_number",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
    )
    op.drop_column("organization", "phone_number")


def downgrade():
    op.add_column(
        "organization",
        sa.Column(
            "phone_number",
            sa.TEXT(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_table("organization_phone_number")
