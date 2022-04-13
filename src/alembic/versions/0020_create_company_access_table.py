"""create company_access table

Revision ID: 0020
Revises: 0019
Create Date: 2022-04-13 14:25:18.323014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = '0020'
down_revision = '0019'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('company_access',
                    sa.Column('id', BINARY(16), nullable=False),
                    sa.Column('ssn', sa.String(length=11), nullable=False),
                    sa.Column('company_id',  BINARY(16), nullable=False),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('ssn', 'company_id')
                    )
    op.create_index(op.f('ix_company_access_company_id_ssn'), 'company_access', ['company_id', 'ssn'], unique=True)


def downgrade():
    op.drop_table('company_access')
