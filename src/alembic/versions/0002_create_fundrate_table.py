"""create fund_rate table

Revision ID: 0002
Revises: 0001
Create Date: 2021-12-01 07:30:27.848794

"""
from alembic import op
from sqlalchemy import Column, DECIMAL, Date
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql.schema import ForeignKey

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'fund_rate',
        Column("id", BINARY(16), primary_key=True, nullable=False),
        Column("fund_id", BINARY(16), ForeignKey('fund.id', name="FK_FUND_RATE_FUND")),
        Column("rate_date", Date),
        Column("rate_close", DECIMAL(19, 6), nullable=False)
    )


def downgrade():
    op.drop_table('fund_rate')
