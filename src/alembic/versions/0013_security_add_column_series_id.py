"""security_add_column_series_id

Revision ID: 0013
Revises: 0012
Create Date: 2022-01-26 15:14:27.369110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('security', sa.Column('series_id', sa.SmallInteger(), nullable=True))


def downgrade():
    op.drop_column('security', 'series_id')
