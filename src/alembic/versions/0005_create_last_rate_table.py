"""create list_rate table

Revision ID: 0005
Revises: 0004
Create Date: 2021-12-06 14:25:18.323014

"""
from alembic import op
from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKeyConstraint, BINARY, DECIMAL

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('last_rate',
                    Column('id', BINARY(16), nullable=False),
                    Column('security_id', BINARY(16), nullable=True),
                    Column('rate_close', DECIMAL(precision=16, scale=6), nullable=True),
                    ForeignKeyConstraint(['security_id'], ['security.id'], ),
                    PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('last_rate')
