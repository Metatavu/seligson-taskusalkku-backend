"""Change kiid_url_fi to nullable

Revision ID: 0017
Revises: 0016
Create Date: 2022-03-17 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0018'
down_revision = '0017'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name="fund", column_name="kiid_url_fi", type_=sa.String(192), nullable=True)


def downgrade():
    op.alter_column(table_name="fund", column_name="kiid_url_fi", type_=sa.String(192), nullable=False)
