"""adding live column to session table

Revision ID: ab4a465da001
Revises: 851067ab3d74
Create Date: 2023-09-22 11:11:38.253761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab4a465da001'
down_revision: Union[str, None] = '851067ab3d74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sessions', sa.Column('live', sa.Boolean(), nullable=False, server_default='FALSE'),)
    pass


def downgrade() -> None:
    op.drop_column('sessions', 'live')
    pass
