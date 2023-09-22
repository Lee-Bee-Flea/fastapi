"""adding strength foundation signups table

Revision ID: 50521a4dfac3
Revises: a9273bfad103
Create Date: 2023-09-18 15:29:39.829019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50521a4dfac3'
down_revision: Union[str, None] = 'a9273bfad103'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('strength_foundation_signups',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('programme_instance_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('squat', sa.Boolean(), nullable=False),
                    sa.Column('deadlift', sa.Boolean(), nullable=False),
                    sa.Column('bench_press', sa.Boolean(), nullable=False),
                    sa.Column('overhead_press', sa.Boolean(), nullable=False),
                    sa.Column('pullup', sa.Boolean(), nullable=False),
                    sa.Column('start_bodyweight', sa.Double(), nullable=False),
                    sa.Column('start_squat_rm', sa.Double()),
                    sa.Column('start_deadlift_rm', sa.Double()),
                    sa.Column('start_bench_press_rm', sa.Double()),
                    sa.Column('start_overhead_press_rm', sa.Double()),
                    sa.Column('start_pullup_rm', sa.Double()),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()'))
                    )
    op.create_foreign_key('strength_foundation_signup_programm/e_instance_fk', 'strength_foundation_signups', 'programme_instances', ['programme_instance_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('strength_foundation_user_fk', 'strength_foundation_signups', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('strength_foundation_signup_programme_instance_fk', 'strength_foundation_signups')
    op.drop_constraint('strength_foundation_user_fk', 'strength_foundation_signups')
    op.drop_table('strength_foundation_signups')
    pass
