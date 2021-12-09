"""create funds table

Revision ID: 0001
Revises: 
Create Date: 2021-11-30 16:35:24.133973

"""

from alembic import op
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'fund',
        Column("id", BINARY(16), primary_key=True, nullable=False),
        Column("fund_id", Integer, index=True, unique=True),
        Column("security_id", String(24), index=True, unique=True),
        Column("security_name_fi", String(191), nullable=False),
        Column("security_name_sv", String(191), nullable=False)
    )


def downgrade():
    op.drop_table('fund')
