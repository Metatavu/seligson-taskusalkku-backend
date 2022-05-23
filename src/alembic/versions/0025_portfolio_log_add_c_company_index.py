"""add index to c_company_id column into portfolio_log table

Revision ID: 0025
Revises: 0024
Create Date: 2022-05-20 17:33:01.160522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0025'
down_revision = '0024'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_portfolio_log_c_company_id'), 'portfolio_log', ['c_company_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_portfolio_log_c_company_id'), table_name='portfolio_log')
