"""create portfolio transaction table

Revision ID: 0008
Revises: 0007
Create Date: 2021-12-06 14:25:18.323014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('portfolio_transaction',
                    sa.Column('id', BINARY(16), nullable=False),
                    sa.Column('transaction_number', sa.Integer(), nullable=False),
                    sa.Column('company_code', sa.String(length=20), nullable=True),
                    sa.Column('portfolio_id', sa.String(length=20), nullable=True),
                    sa.Column('security_id', sa.String(length=20), nullable=True),
                    sa.Column('transaction_date', sa.Date(), nullable=True),
                    sa.Column('amount', sa.DECIMAL(precision=19, scale=6), nullable=True),
                    sa.Column('purchase_c_value', sa.DECIMAL(precision=15, scale=2), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('transaction_number')
                    )
    op.create_index(op.f('ix_portfolio_transaction_company_code'), 'portfolio_transaction', ['company_code'],
                    unique=False)
    op.create_index(op.f('ix_portfolio_transaction_portfolio_id'), 'portfolio_transaction', ['portfolio_id'],
                    unique=False)
    op.create_index(op.f('ix_portfolio_transaction_security_id'), 'portfolio_transaction', ['security_id'],
                    unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_portfolio_transaction_security_id'), table_name='portfolio_transaction')
    op.drop_index(op.f('ix_portfolio_transaction_portfolio_id'), table_name='portfolio_transaction')
    op.drop_index(op.f('ix_portfolio_transaction_company_code'), table_name='portfolio_transaction')
    op.drop_table('portfolio_transaction')
    # ### end Alembic commands ###