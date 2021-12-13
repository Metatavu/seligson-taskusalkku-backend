"""create funds table

Revision ID: 0001
Revises: 
Create Date: 2021-11-30 16:35:24.133973

"""

from alembic import op
from sqlalchemy import Column, PrimaryKeyConstraint, BINARY, Integer

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('fund',
                    Column('id', BINARY(16), nullable=False),
                    Column('original_id', Integer(), nullable=True),
                    PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_fund_original_id'), 'fund', ['original_id'], unique=True)


def downgrade():
    op.drop_table('fund')
