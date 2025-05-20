"""Create building table

Revision ID: 97690affcdf0
Revises:
Create Date: 2025-05-20 15:06:53.166227+00:00
"""

import geoalchemy2.types
import sqlalchemy as sa
from alembic import op

revision = "97690affcdf0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "building",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    # Index is created automatically by PostGIS
    op.drop_index(
        "idx_building_location",
        table_name="building",
        postgresql_using="gist",
    )

    op.drop_table("building")
