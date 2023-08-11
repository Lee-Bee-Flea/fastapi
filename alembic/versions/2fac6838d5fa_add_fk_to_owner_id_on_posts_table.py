"""add FK to owner_id on posts table

Revision ID: 2fac6838d5fa
Revises: 3153361501c3
Create Date: 2023-08-11 10:48:33.677489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fac6838d5fa'
down_revision: Union[str, None] = '3153361501c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key('post_users_fk', 'posts', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('post_users_fk', 'posts')
    pass
