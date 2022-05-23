"""add foreign key to c_company_id column of portfolio_log

Revision ID: 0024
Revises: 0023
Create Date: 2022-05-20 17:33:01.160522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0024'
down_revision = '0023'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        constraint_name="fk_portfolio_log_c_company_id",
        source_table='portfolio_log',
        referent_table="company",
        local_cols=['c_company_id'],
        remote_cols=['id']
    )


def downgrade():
    op.drop_constraint('fk_portfolio_log_c_company_id', 'portfolio_log')
