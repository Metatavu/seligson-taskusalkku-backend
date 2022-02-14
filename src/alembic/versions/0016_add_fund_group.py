"""add fund group column to fund table

Revision ID: 0016
Revises: 0015
Create Date: 2022-02-14 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("fund", sa.Column("fund_group", sa.String(192), nullable=True))
    op.execute("UPDATE fund SET fund_group = 'ACTIVE' WHERE original_id in ('3333','88476','88537','8888')")
    op.execute("UPDATE fund SET fund_group = 'BALANCED' WHERE original_id in ('818419')")
    op.execute("UPDATE fund SET fund_group = 'FIXED_INCOME' WHERE original_id in ('1111','2222','580')")
    op.execute("UPDATE fund SET fund_group = 'DIMENSION' WHERE original_id in ('DIMESCB','DIMUSCB','DIMEMVB')")
    op.execute("UPDATE fund SET fund_group = 'SPILTAN' WHERE original_id in ('SPILTAN SVERIGE','SPILTAN STABIL')")
    op.execute("UPDATE fund SET fund_group = 'PASSIVE' WHERE original_id in ('800','5555','818423','7777','795',"
               "'88511','581','4444')")


def downgrade():
    op.drop_column("fund", column_name="fund_group")
