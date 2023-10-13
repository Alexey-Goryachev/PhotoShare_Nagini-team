"""Create User and Photo tables

Revision ID: 19481ccfad09
Revises: 50077d3469d6
Create Date: 2023-10-13 17:29:04.100325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19481ccfad09'
down_revision: Union[str, None] = '50077d3469d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
