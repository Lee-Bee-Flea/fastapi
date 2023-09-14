"""adding programmes table

Revision ID: 802768af4b44
Revises: 9b8f1876b7b4
Create Date: 2023-09-14 12:03:39.486169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '802768af4b44'
down_revision: Union[str, None] = '9b8f1876b7b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('programmes',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('version', sa.String(), nullable=False),
                    sa.Column('goals', sa.ARRAY(sa.String)),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    )
    pass


def downgrade() -> None:
    op.drop_table('programmes')
    pass
