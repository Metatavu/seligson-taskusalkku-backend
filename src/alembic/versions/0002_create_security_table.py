"""create funds table

Revision ID: 0001
Revises: 
Create Date: 2021-11-30 16:35:24.133973

"""

from alembic import op
from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKeyConstraint, BINARY, String, CHAR

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('security',
                    Column('id', BINARY(16), nullable=False),
                    Column('original_id', String(length=20), nullable=True),
                    Column('currency', CHAR(length=3), nullable=True),
                    Column('name_fi', String(length=191), nullable=False),
                    Column('name_sv', String(length=191), nullable=False),
                    Column('fund_id', BINARY(16), nullable=True),
                    ForeignKeyConstraint(['fund_id'], ['fund.id'], ),
                    PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_security_original_id'), 'security', ['original_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_security_original_id'), table_name='security')
    op.drop_table('security')
