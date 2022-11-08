"""add content column to posts table

Revision ID: 34522379292a
Revises: 5fae2f9157c0
Create Date: 2022-11-08 23:03:14.857021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34522379292a'
down_revision = '5fae2f9157c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    pass
