"""empty message

Revision ID: a4ac210afb75
Revises: d3809c8911d1
Create Date: 2023-10-13 17:20:31.454917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4ac210afb75'
down_revision: Union[str, None] = 'd3809c8911d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
