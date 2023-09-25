"""adding user physiology table

Revision ID: 4f67d600c603
Revises: 9938c5f5d1bb
Create Date: 2023-09-24 10:16:07.863862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f67d600c603'
down_revision: Union[str, None] = '9938c5f5d1bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_physiology',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('measure_type', sa.String(), nullable=False),
                    sa.Column('measure_unit', sa.String(), nullable=False),
                    sa.Column('measure', sa.Double(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')))
    
    op.create_foreign_key('user_physiology_user_fk', 'user_physiology', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('user_physiology_user_fk', 'user_physiology')
    op.drop_table('user_physiology')
    pass
