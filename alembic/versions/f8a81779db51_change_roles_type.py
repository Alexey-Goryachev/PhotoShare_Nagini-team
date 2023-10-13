"""change_roles_type

Revision ID: f8a81779db51
Revises: 100eb9aacc0d
Create Date: 2023-10-13 16:31:53.295917

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f8a81779db51'
down_revision: Union[str, None] = '100eb9aacc0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Використовуйте alter_column для зміни типу і вказівки USING
    op.alter_column('users', 'roles', type_=sa.Enum(
        'user', 'admin', name='user_role'), using='roles::user_role')


def downgrade():
    # В зворотному випадку, ви можете використовувати операцію без using
    op.alter_column('users', 'roles', type_=sa.Enum(
        'user', 'admin', name='user_role'))
