"""create company table

Revision ID: 0003
Revises: 0002
Create Date: 2021-12-06 14:25:18.323014

"""
from sqlalchemy import BINARY, String

from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('company',
                    sa.Column('id', BINARY(16), nullable=False),
                    sa.Column('original_id', String(length=20), nullable=True),
                    sa.Column('ssn', String(length=11), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_company_original_id'), 'company', ['original_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_company_original_id'), table_name='company')
    op.drop_table('company')
