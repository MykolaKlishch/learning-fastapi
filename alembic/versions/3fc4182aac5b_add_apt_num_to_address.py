"""add apt_num to address

Revision ID: 3fc4182aac5b
Revises: de3ff0eb4e62
Create Date: 2022-07-11 21:05:20.157139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fc4182aac5b'
down_revision = 'de3ff0eb4e62'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')

