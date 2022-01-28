"""security_add_column_update

Revision ID: 0014
Revises: 0013
Create Date: 2022-01-27 17:33:01.160522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('security', sa.Column('updated', sa.DateTime(), server_default='1970-01-01', nullable=True))
    op.create_index(op.f('ix_security_updated'), 'security', ['updated'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_security_updated'), table_name='security')
    op.drop_column('security', 'updated')
