"""add name column to portfolio table

Revision ID: 0008
Revises: 0007
Create Date: 2021-12-17 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('portfolio', sa.Column('name', sa.String(192), nullable=False, default="UNDEFINED"))


def downgrade():
    op.drop_column("portfolio", column_name="name")
