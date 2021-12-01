"""create FundRate table

Revision ID: fc1166e7bafa
Revises: 3be52b1b9a8b
Create Date: 2021-12-01 07:30:27.848794

"""
from alembic import op
from sqlalchemy import Column, DECIMAL, Integer, String, Date
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql.schema import ForeignKey


# revision identifiers, used by Alembic.
revision = 'fc1166e7bafa'
down_revision = '3be52b1b9a8b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'fund_rate',
        Column("id", BINARY(16), primary_key=True, nullable=False),
        Column("fund_id", BINARY(16), ForeignKey('fund.id')),
        Column("rate_date", Date),
        Column("rate_close", DECIMAL(19, 6), nullable=False)
    )

def downgrade():
    op.drop_table('fund_rate')
