"""create_tables

Revision ID: 594d961d7cc8
Revises: 
Create Date: 2021-12-09 12:03:25.387829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '594d961d7cc8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('original_id', sa.String(length=20), nullable=True),
    sa.Column('ssn', sa.String(length=11), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_original_id'), 'company', ['original_id'], unique=True)
    op.create_table('fund',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('original_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fund_original_id'), 'fund', ['original_id'], unique=True)
    op.create_table('portfolio',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('original_id', sa.String(length=20), nullable=True),
    sa.Column('company_id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('original_id')
    )
    op.create_index(op.f('ix_portfolio_company_id'), 'portfolio', ['company_id'], unique=False)
    op.create_table('security',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('original_id', sa.String(length=20), nullable=True),
    sa.Column('currency', sa.CHAR(length=3), nullable=True),
    sa.Column('name_fi', sa.String(length=191), nullable=False),
    sa.Column('name_sv', sa.String(length=191), nullable=False),
    sa.Column('fund_id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=True),
    sa.ForeignKeyConstraint(['fund_id'], ['fund.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_security_original_id'), 'security', ['original_id'], unique=True)
    op.create_table('fund_rate',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('security_id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=True),
    sa.Column('rate_date', sa.Date(), nullable=True),
    sa.Column('rate_close', sa.DECIMAL(precision=19, scale=6), nullable=False),
    sa.ForeignKeyConstraint(['security_id'], ['security.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('last_rate',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('security_id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=True),
    sa.Column('rate_close', sa.DECIMAL(precision=16, scale=6), nullable=True),
    sa.ForeignKeyConstraint(['security_id'], ['security.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('portfolio_log',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('transaction_number', sa.Integer(), nullable=True),
    sa.Column('transaction_code', sa.CHAR(length=2), nullable=True),
    sa.Column('transaction_date', sa.DateTime(), nullable=True),
    sa.Column('c_total_value', sa.DECIMAL(precision=15, scale=2), nullable=True),
    sa.Column('portfolio_id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=True),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolio_log_portfolio_id'), 'portfolio_log', ['portfolio_id'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_code'), 'portfolio_log', ['transaction_code'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_date'), 'portfolio_log', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_portfolio_log_transaction_number'), 'portfolio_log', ['transaction_number'], unique=True)
    op.create_table('portfolio_transaction',
    sa.Column('id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=False),
    sa.Column('transaction_number', sa.Integer(), nullable=True),
    sa.Column('transaction_date', sa.DateTime(), nullable=True),
    sa.Column('amount', sa.DECIMAL(precision=19, scale=6), nullable=True),
    sa.Column('purchase_c_value', sa.DECIMAL(precision=15, scale=2), nullable=True),
    sa.Column('portfolio_id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=True),
    sa.Column('security_id', database.sqlalchemy_uuid.SqlAlchemyUuid(length=16), nullable=True),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], ),
    sa.ForeignKeyConstraint(['security_id'], ['security.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transaction_number')
    )
    op.create_index(op.f('ix_portfolio_transaction_portfolio_id'), 'portfolio_transaction', ['portfolio_id'], unique=False)
    op.create_index(op.f('ix_portfolio_transaction_security_id'), 'portfolio_transaction', ['security_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_portfolio_transaction_security_id'), table_name='portfolio_transaction')
    op.drop_index(op.f('ix_portfolio_transaction_portfolio_id'), table_name='portfolio_transaction')
    op.drop_table('portfolio_transaction')
    op.drop_index(op.f('ix_portfolio_log_transaction_number'), table_name='portfolio_log')
    op.drop_index(op.f('ix_portfolio_log_transaction_date'), table_name='portfolio_log')
    op.drop_index(op.f('ix_portfolio_log_transaction_code'), table_name='portfolio_log')
    op.drop_index(op.f('ix_portfolio_log_portfolio_id'), table_name='portfolio_log')
    op.drop_table('portfolio_log')
    op.drop_table('last_rate')
    op.drop_table('fund_rate')
    op.drop_index(op.f('ix_security_original_id'), table_name='security')
    op.drop_table('security')
    op.drop_index(op.f('ix_portfolio_company_id'), table_name='portfolio')
    op.drop_table('portfolio')
    op.drop_index(op.f('ix_fund_original_id'), table_name='fund')
    op.drop_table('fund')
    op.drop_index(op.f('ix_company_original_id'), table_name='company')
    op.drop_table('company')
    # ### end Alembic commands ###