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
                    sa.Column('id', sa.BINARY(length=16), nullable=False),
                    sa.Column('transaction_number', sa.Integer(), nullable=True),
                    sa.Column('transaction_code', sa.CHAR(length=2), nullable=True),
                    sa.Column('transaction_date', sa.Date(), nullable=True),
                    sa.Column('c_total_value', sa.DECIMAL(precision=15, scale=2), nullable=True),
                    sa.Column('portfolio_id', sa.BINARY(length=16), nullable=False),
                    sa.Column('security_id', sa.BINARY(length=16), nullable=False),
                    sa.Column('c_security_id', sa.BINARY(length=16), nullable=True),
                    sa.Column('amount', sa.DECIMAL(precision=19, scale=6), nullable=False),
                    sa.Column('c_price', sa.DECIMAL(precision=19, scale=6), nullable=False),
                    sa.Column('payment_date', sa.Date(), nullable=True),
                    sa.Column('c_value', sa.DECIMAL(precision=15, scale=2), nullable=False),
                    sa.Column('provision', sa.DECIMAL(precision=15, scale=2), nullable=True),
                    sa.Column('status', sa.CHAR(length=1), nullable=False),
                    sa.ForeignKeyConstraint(['c_security_id'], ['security.id'], ),
                    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], ),
                    sa.ForeignKeyConstraint(['security_id'], ['security.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_portfolio_log_c_security_id'), 'portfolio_log', ['c_security_id'], unique=False)
    op.create_index(op.f('ix_portfolio_log_payment_date'), 'portfolio_log', ['payment_date'], unique=False)
    op.create_index(op.f('ix_portfolio_log_portfolio_id'), 'portfolio_log', ['portfolio_id'], unique=False)
    op.create_index(op.f('ix_portfolio_log_security_id'), 'portfolio_log', ['security_id'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_code'), 'portfolio_log', ['transaction_code'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_date'), 'portfolio_log', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_number'), 'portfolio_log', ['transaction_number'], unique=True)


def downgrade():
    op.drop_table('portfolio_log')
