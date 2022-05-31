"""create synchronization_failure table

Revision ID: 0021
Revises: 0020
Create Date: 2022-04-21 14:25:18.323014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0021'
down_revision = '0020'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('synchronization_failure',
                    sa.Column('id', BINARY(16), nullable=False),
                    sa.Column('original_id', sa.String(length=191), nullable=False),
                    sa.Column('message',  sa.String(length=191), nullable=False),
                    sa.Column('origin_task',  sa.String(length=191), nullable=False),
                    sa.Column('target_task', sa.String(length=191), nullable=False),
                    sa.Column('action',  sa.Integer, nullable=False),
                    sa.Column('handled',  sa.Boolean, nullable=False),
                    sa.Column('created',  sa.DateTime, nullable=False),
                    sa.Column('updated',  sa.DateTime, nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('synchronization_failure')