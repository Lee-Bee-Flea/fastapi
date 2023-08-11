"""add foreign-key to posts table

Revision ID: 3153361501c3
Revises: 1bc577f6c99c
Create Date: 2023-08-11 10:16:33.547405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3153361501c3'
down_revision: Union[str, None] = '1bc577f6c99c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'owner_id')
    pass
