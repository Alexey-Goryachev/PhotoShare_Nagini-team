"""empty message

Revision ID: 6775a9e306a7
Revises: a4ac210afb75
Create Date: 2023-10-13 17:23:52.717646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6775a9e306a7'
down_revision: Union[str, None] = 'a4ac210afb75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
