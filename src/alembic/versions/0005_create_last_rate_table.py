"""create list_rate table

Revision ID: 0005
Revises: 0004
Create Date: 2021-12-06 14:25:18.323014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('last_rate',
                    sa.Column('id', BINARY(16), nullable=False),
                    sa.Column('security_id', sa.String(length=20), nullable=True),
                    sa.Column('rate_close', sa.DECIMAL(precision=16, scale=6), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_last_rate_security_id'), 'last_rate', ['security_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_last_rate_security_id'), table_name='last_rate')
    op.drop_table('last_rate')
    # ### end Alembic commands ###