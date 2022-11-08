"""add last few columns

Revision ID: 4ca16b5e9611
Revises: 532a17db5625
Create Date: 2022-11-08 23:04:38.087002

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ca16b5e9611'
down_revision = '532a17db5625'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('published', sa.Boolean(), nullable=False, server_default='True'))
    op.add_column('posts', sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                                     nullable=False, server_default=sa.text('now()')))
    pass


def downgrade() -> None:
    pass
