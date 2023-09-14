"""adding programme_instances table

Revision ID: 9b8f1876b7b4
Revises: c9aad6311cd9
Create Date: 2023-09-14 11:51:10.796413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b8f1876b7b4'
down_revision: Union[str, None] = 'c9aad6311cd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('programme_instances',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('programme_id', sa.Integer(), nullable=False),
                    sa.Column('start_at', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
                    sa.Column('cancelled_at', sa.TIMESTAMP(timezone=True)),
                    sa.Column('status', sa.String(), nullable=False),
                    sa.Column('cancelled_reason', sa.String()),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    )
    pass


def downgrade() -> None:
    op.drop_table('programme_instances')
    pass
