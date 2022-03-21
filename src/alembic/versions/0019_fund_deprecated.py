"""Add deprecated column to fund table

Revision ID: 0017
Revises: 0016
Create Date: 2022-03-17 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0019'
down_revision = '0018'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("fund", sa.Column("deprecated", sa.Boolean, nullable=False))
    op.execute("UPDATE fund SET deprecated = false")


def downgrade():
    op.drop_column(table_name="fund", column_name="deprecated")
