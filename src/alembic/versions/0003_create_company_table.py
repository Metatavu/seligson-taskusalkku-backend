"""create company table

Revision ID: 0003
Revises: 0002
Create Date: 2021-12-06 14:25:18.323014

"""
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy import Column, Integer, String
import sqlalchemy as sa

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
                    sa.Column('id', BINARY(16), nullable=False),
                    sa.Column('company_code', sa.String(length=20), nullable=True),
                    sa.Column('user_id', BINARY(16), nullable=True),
                    sa.Column('user_id', BINARY(16), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_company_company_code'), 'company', ['company_code'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_company_company_code'), table_name='company')
    op.drop_table('company')
    # ### end Alembic commands ###
