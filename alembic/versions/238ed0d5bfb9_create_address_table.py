"""create address table

Revision ID: 238ed0d5bfb9
Revises: 944e01a76309
Create Date: 2022-07-11 19:02:37.738874

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '238ed0d5bfb9'
down_revision = '944e01a76309'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('address',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('address1', sa.String(), nullable=False),
                    sa.Column('address2', sa.String(), nullable=False),
                    sa.Column('city', sa.String(), nullable=False),
                    sa.Column('state', sa.String(), nullable=False),
                    sa.Column('country', sa.String(), nullable=False),
                    sa.Column('postal_code', sa.String(), nullable=False),
                    sa.Column('city', sa.String(), nullable=False),

                    )


def downgrade() -> None:
    op.drop_table('address')
