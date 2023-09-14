"""adding sets table

Revision ID: 31fe3c2f0db3
Revises: d5b717a3295d
Create Date: 2023-09-13 22:16:44.133070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31fe3c2f0db3'
down_revision: Union[str, None] = 'd5b717a3295d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('sets',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('set_group_id', sa.Integer()),
                    sa.Column('set_group_rank', sa.Integer()),
                    sa.Column('weight', sa.Double(), nullable=False),
                    sa.Column('repetitions', sa.Integer(), nullable=False),
                    sa.Column('rir', sa.Integer()),
                    sa.Column('epley', sa.Double()),
                    sa.Column('brzycki', sa.Double()),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    )
    pass


def downgrade() -> None:
    op.drop_table('sets')
    pass
