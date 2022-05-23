"""add index to c_company_id column of portfolio_log

Revision ID: 0023
Revises: 0022
Create Date: 2022-05-20 17:33:01.160522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0023'
down_revision = '0022'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('portfolio_log', sa.Column('c_company_id', sa.BINARY(length=16), nullable=True))


def downgrade():
    op.drop_column('portfolio_log', 'c_company_id')
