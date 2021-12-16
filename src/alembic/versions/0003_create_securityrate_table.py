"""create security_rate table

Revision ID: 0002
Revises: 0001
Create Date: 2021-12-01 07:30:27.848794

"""
from alembic import op
from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKeyConstraint, BINARY, Date, DECIMAL

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('security_rate',
                    Column('id', BINARY(16), nullable=False),
                    Column('security_id', BINARY(16), nullable=False),
                    Column('rate_date', Date(), nullable=True),
                    Column('rate_close', DECIMAL(precision=19, scale=6), nullable=False),
                    ForeignKeyConstraint(['security_id'], ['security.id'], ),
                    PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_security_rate_security_id_rate_date', 'security_rate', ['security_id', 'rate_date'], unique=True)


def downgrade():
    op.drop_table('security_rate')
