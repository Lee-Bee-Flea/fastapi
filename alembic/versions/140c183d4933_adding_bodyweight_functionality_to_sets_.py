"""adding bodyweight functionality to sets, set_groups, and exercises tables

Revision ID: 140c183d4933
Revises: 4f67d600c603
Create Date: 2023-09-24 10:39:13.209531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '140c183d4933'
down_revision: Union[str, None] = '4f67d600c603'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sets', sa.Column('bodyweight', sa.Boolean(), nullable=False, server_default='FALSE'))
    op.add_column('sets', sa.Column('bodyweight_measure', sa.Double()))
    op.add_column('sets', sa.Column('bodyweight_ratio', sa.Double()))
    op.add_column('set_groups', sa.Column('bodyweight', sa.Boolean(), nullable=False, server_default='FALSE'))
    op.add_column('exercises', sa.Column('bodyweight_ratio', sa.Double()))
    pass


def downgrade() -> None:
    op.drop_column('sets', 'bodyweight')
    op.drop_column('sets', 'bodyweight_measure')
    op.drop_column('sets', 'bodyweight_ratio')
    op.drop_column('set_groups', 'bodyweight')
    op.drop_column('exercises', 'bodyweight_ratio')
    pass
