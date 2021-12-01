"""create funds table

Revision ID: 3be52b1b9a8b
Revises: 
Create Date: 2021-11-30 16:35:24.133973

"""

from alembic import op
from sqlalchemy import Column, DECIMAL, Integer, String
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '3be52b1b9a8b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'Fund',
        Column("id", BINARY(16), primary_key=True, nullable=False),
        Column("fundId", Integer, index=True, unique=True),
        Column("securityId", String(24), index=True, unique=True),
        Column("securityNameFi", String(191), nullable=False),
        Column("securityNameSv", String(191), nullable=False),
        Column("classType", String(191), nullable=False),
        Column("minimumPurchase", DECIMAL(19, 6), nullable=False, default=0.000)
    )


def downgrade():
    op.drop_table('Fund')
