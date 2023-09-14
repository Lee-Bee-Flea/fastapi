"""adding set_groups table

Revision ID: 3a6cfeab283a
Revises: 31fe3c2f0db3
Create Date: 2023-09-14 10:52:47.905064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a6cfeab283a'
down_revision: Union[str, None] = '31fe3c2f0db3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('set_groups',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('session_id', sa.Integer()),
                    sa.Column('exercise_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    )
    pass


def downgrade() -> None:
    op.drop_table('set_groups')
    pass
