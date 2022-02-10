"""add name_en column to security

Revision ID: 0014
Revises: 0013
Create Date: 2022-01-27 17:33:01.160522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('security', sa.Column('name_en', sa.String(length=191), nullable=True))
    op.execute("UPDATE security SET updated = DATE('1970-01-01')")


def downgrade():
    op.drop_column('security', 'name_en')
