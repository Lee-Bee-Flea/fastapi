"""adding rep_max column to set table blending epley and brzycki

Revision ID: 9938c5f5d1bb
Revises: fec00e2486aa
Create Date: 2023-09-23 10:00:47.112169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9938c5f5d1bb'
down_revision: Union[str, None] = 'fec00e2486aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sets', sa.Column('rep_max', sa.Double()))
    pass


def downgrade() -> None:
    op.drop_column('sets', 'rep_max')
    pass
