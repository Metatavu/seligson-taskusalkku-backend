"""create portfolio table

Revision ID: 0006
Revises: 0005
Create Date: 2021-12-06 14:25:18.323014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('portfolio',
                    sa.Column('id', BINARY(16), nullable=False),
                    sa.Column('original_id', sa.String(length=20), nullable=False),
                    sa.Column('company_id',  BINARY(16), nullable=False),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('original_id')
                    )
    op.create_index(op.f('ix_portfolio_company_id'), 'portfolio', ['company_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_portfolio_company_id'), table_name='portfolio')
    op.drop_table('portfolio')
