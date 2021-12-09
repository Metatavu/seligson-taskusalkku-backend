"""create security table

Revision ID: 0004
Revises: 0003
Create Date: 2021-12-06 14:25:18.323014

"""
from alembic import op
from sqlalchemy import Column, PrimaryKeyConstraint, String, BINARY, DECIMAL

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('security',
                    Column('id', BINARY(16), nullable=False),
                    Column('security_id', String(length=20), nullable=False),
                    Column('currency', CHAR(length=3), nullable=True),
                    Column('pe_corr', DECIMAL(precision=8, scale=4), nullable=True),
                    Column('isin', String(length=12), nullable=True),
                    PrimaryKeyConstraint('id', 'security_id')
                    )
    op.create_index(op.f('ix_security_security_id'), 'security', ['security_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_security_security_id'), table_name='security')
    op.drop_table('security')
