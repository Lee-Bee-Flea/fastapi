"""adding FKs to set_groups, sessions & programme_instances

Revision ID: 23f764df4661
Revises: 7125385cf405
Create Date: 2023-09-14 12:17:28.543177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23f764df4661'
down_revision: Union[str, None] = '7125385cf405'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key('set_groups_session_fk', 'set_groups', 'sessions', ['session_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('set_groups_exercise_fk', 'set_groups', 'exercises', ['exercise_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('sessions_programme_instance_fk', 'sessions', 'programme_instances', ['programme_instance_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('programme_instance_user_fk', 'programme_instances', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('programme_instance_programme_fk', 'programme_instances', 'programmes', ['programme_id'], ['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('set_groups_session_fk', 'set_groups')
    op.drop_constraint('set_groups_exercise_fk', 'set_groups')
    op.drop_constraint('sessions_programme_instance_fk', 'sessions')
    op.drop_constraint('programme_instance_user_fk', 'programme_instances')
    # op.drop_constraint('programme_instance_programme_fk', 'programme_instances')
    pass
