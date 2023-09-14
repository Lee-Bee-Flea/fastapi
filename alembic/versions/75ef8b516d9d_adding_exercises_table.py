"""adding exercises table

Revision ID: 75ef8b516d9d
Revises: 3a6cfeab283a
Create Date: 2023-09-14 11:36:24.829677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75ef8b516d9d'
down_revision: Union[str, None] = '3a6cfeab283a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('exercises',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('name', sa.String()),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),)
    pass


def downgrade() -> None:
    op.drop_table('exercises')
    pass
