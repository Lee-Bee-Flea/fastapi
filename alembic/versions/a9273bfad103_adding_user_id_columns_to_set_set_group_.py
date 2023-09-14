"""adding user_id columns to set, set_group and session tables + FKs

Revision ID: a9273bfad103
Revises: 23f764df4661
Create Date: 2023-09-14 12:54:43.206604

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9273bfad103'
down_revision: Union[str, None] = '23f764df4661'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sets', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('set_groups', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('sessions', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('set_user_fk', 'sets', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('set_group_user_fk', 'set_groups', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('session_user_fk', 'sessions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('set_user_fk', 'sets')
    op.drop_constraint('set_group_user_fk', 'set_groups')
    op.drop_constraint('session_user_fk', 'sessions')
    op.drop_column('sets', 'user_id')
    op.drop_column('set_groups', 'user_id')
    op.drop_column('sessions', 'user_id')
    pass
