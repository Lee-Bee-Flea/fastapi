"""adding sessions table

Revision ID: c9aad6311cd9
Revises: 75ef8b516d9d
Create Date: 2023-09-14 11:45:04.362957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9aad6311cd9'
down_revision: Union[str, None] = '75ef8b516d9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('sessions',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('programme_instance_id', sa.Integer()),
                    sa.Column('start_at', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('end_at', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    )
    pass


def downgrade() -> None:
    op.drop_table('sessions')
    pass
