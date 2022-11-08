"""add foreign key to posts table

Revision ID: 532a17db5625
Revises: b6602519f73e
Create Date: 2022-11-08 23:04:11.575928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '532a17db5625'
down_revision = 'b6602519f73e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('posts_users_fk', source_table="posts", referent_table="users",
                          local_cols=['owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    pass
