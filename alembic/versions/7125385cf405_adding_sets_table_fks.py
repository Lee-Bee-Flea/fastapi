"""adding sets table FKs

Revision ID: 7125385cf405
Revises: 802768af4b44
Create Date: 2023-09-14 12:09:07.252658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7125385cf405'
down_revision: Union[str, None] = '802768af4b44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key('sets_set_group_fk', 'sets', 'set_groups', ['set_group_id'], ['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('sets_set_group_fk', 'sets')
    pass
