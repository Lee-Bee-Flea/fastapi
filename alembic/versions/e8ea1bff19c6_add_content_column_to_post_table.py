"""add content column to post table

Revision ID: e8ea1bff19c6
Revises: 09e21be4f2d5
Create Date: 2023-08-11 09:58:14.292447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8ea1bff19c6'
down_revision: Union[str, None] = '09e21be4f2d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
