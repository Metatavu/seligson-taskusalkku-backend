"""add updated columns to portfolio_log and portfolio_transaction tables

Revision ID: 0008
Revises: 0007
Create Date: 2021-12-17 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("portfolio_log", sa.Column("updated", sa.DateTime, nullable=False))
    op.add_column("portfolio_transaction", sa.Column("updated", sa.DateTime, nullable=False))
    op.create_index("ix_portfolio_log_security_id_updated", "portfolio_log", ["security_id", "updated"])
    op.create_index("ix_portfolio_transaction_security_id_updated", "portfolio_transaction", ["security_id", "updated"])


def downgrade():
    op.drop_column("portfolio_log", column_name="updated")
    op.drop_column("portfolio_transaction", column_name="updated")
