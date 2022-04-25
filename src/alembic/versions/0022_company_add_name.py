"""add name column to company table

Revision ID: 0022
Revises: 0021
Create Date: 2022-04-25 17:33:01.160522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0022'
down_revision = '0021'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('company', sa.Column('name', sa.String(length=191), nullable=False))
    op.execute("UPDATE company SET name = 'UNKNOWN', updated = DATE('1970-01-01')")


def downgrade():
    op.drop_column('company', 'name')
