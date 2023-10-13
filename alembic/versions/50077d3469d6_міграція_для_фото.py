"""Міграція для фото

Revision ID: 50077d3469d6
Revises: 6775a9e306a7
Create Date: 2023-10-13 17:25:52.654529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50077d3469d6'
down_revision: Union[str, None] = '6775a9e306a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
