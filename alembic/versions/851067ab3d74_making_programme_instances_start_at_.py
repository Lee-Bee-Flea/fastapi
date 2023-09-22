"""making programme instances start_at column auto set to now()

Revision ID: 851067ab3d74
Revises: 50521a4dfac3
Create Date: 2023-09-19 11:11:01.777864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '851067ab3d74'
down_revision: Union[str, None] = '50521a4dfac3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('programme_instances', column_name='start_at', server_default=sa.text('NOW()'))
    pass


def downgrade() -> None:
    op.alter_column('programme_instances', 'start_at', server_default=False)
    pass
