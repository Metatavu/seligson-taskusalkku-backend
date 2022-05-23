"""add c_company_id column to portfolio_log table

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
    op.execute('SET FOREIGN_KEY_CHECKS=0')

    op.add_column('portfolio_log', sa.Column('c_company_id', sa.BINARY(length=16), nullable=True))

    op.create_foreign_key(
        constraint_name="fk_portfolio_log_c_company_id",
        source_table='portfolio_log',
        referent_table="company",
        local_cols=['c_company_id'],
        remote_cols=['id']
    )

    op.create_index(op.f('ix_portfolio_log_c_company_id'), 'portfolio_log', ['c_company_id'], unique=False)

    op.execute('SET FOREIGN_KEY_CHECKS=1')


def downgrade():
    op.drop_constraint('fk_portfolio_log_c_company_id', 'portfolio_log')
    op.drop_index(op.f('ix_portfolio_log_c_company_id'), table_name='portfolio_log')
    op.drop_column('portfolio_log', 'c_company_id')
