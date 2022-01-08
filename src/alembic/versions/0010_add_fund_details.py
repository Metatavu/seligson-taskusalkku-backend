"""add kiid url and risk_level columns to funds table

Revision ID: 0008
Revises: 0007
Create Date: 2021-12-17 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("fund", sa.Column("risk_level", sa.String(192), nullable=True))
    op.add_column('fund', sa.Column("kiid_url_fi", sa.String(192), nullable=False, server_default="UNDEFINED"))
    op.add_column('fund', sa.Column("kiid_url_sv", sa.String(192), nullable=True))
    op.add_column('fund', sa.Column("kiid_url_en", sa.String(192), nullable=True))


def downgrade():
    op.drop_column("fund", column_name="risk_level")
    op.drop_column("fund", column_name="kiid_url_fi")
    op.drop_column("fund", column_name="kiid_url_sv")
    op.drop_column("fund", column_name="kiid_url_en")
