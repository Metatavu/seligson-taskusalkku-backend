"""create log table

Revision ID: 0007
Revises: 0006
Create Date: 2021-12-06 14:25:18.323014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('portfolio_log',
                    sa.Column('id',  BINARY(16), nullable=False),
                    sa.Column('transaction_number', sa.Integer(), nullable=True),
                    sa.Column('transaction_code', sa.CHAR(length=2), nullable=True),
                    sa.Column('transaction_date', sa.DateTime(), nullable=True),
                    sa.Column('c_total_value', sa.DECIMAL(precision=15, scale=2), nullable=True),
                    sa.Column('portfolio_id',  BINARY(16), nullable=False),
                    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_portfolio_log_portfolio_id'), 'portfolio_log', ['portfolio_id'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_code'), 'portfolio_log', ['transaction_code'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_date'), 'portfolio_log', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_number'), 'portfolio_log', ['transaction_number'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_portfolio_log_transaction_number'), table_name='portfolio_log')
    op.drop_index(op.f('ix_portfolio_log_transaction_date'), table_name='portfolio_log')
    op.drop_index(op.f('ix_portfolio_log_transaction_code'), table_name='portfolio_log')
    op.drop_index(op.f('ix_portfolio_log_portfolio_id'), table_name='portfolio_log')
    op.drop_table('portfolio_log')
