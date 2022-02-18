"""add updated column to company table

Revision ID: 0017
Revises: 0016
Create Date: 2022-02-18 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0017'
down_revision = '0016'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("company", sa.Column("updated", sa.DateTime, nullable=False))


def downgrade():
    op.drop_column("company", column_name="updated")
