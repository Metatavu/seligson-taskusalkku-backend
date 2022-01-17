"""add rate_date column to last_rate table

Revision ID: 0012
Revises: 0011
Create Date: 2021-12-17 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("last_rate", sa.Column("rate_date", sa.Date, nullable=False))
    op.create_index("ix_last_rate_security_id_rate_date", "last_rate", ["security_id", "rate_date"])


def downgrade():
    op.drop_column("last_rate", column_name="rate_date")
