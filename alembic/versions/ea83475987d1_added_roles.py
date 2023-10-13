"""Added roles

Revision ID: ea83475987d1
Revises: dd4a467b34d2
Create Date: 2023-10-11 19:16:56.669939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea83475987d1'
down_revision: Union[str, None] = 'dd4a467b34d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('roles', sa.String(length=20), nullable=True))
    op.drop_column('users', 'role')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.drop_column('users', 'roles')
    # ### end Alembic commands ###