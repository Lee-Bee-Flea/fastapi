"""adding exercise type column

Revision ID: fec00e2486aa
Revises: ab4a465da001
Create Date: 2023-09-22 11:43:05.446718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fec00e2486aa'
down_revision: Union[str, None] = 'ab4a465da001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('exercises', sa.Column('type', sa.String()),)
    pass


def downgrade() -> None:
    op.drop_column('exercises', 'type')
    pass
