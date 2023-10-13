"""назва_вашої_міграції

Revision ID: d3809c8911d1
Revises: f8a81779db51
Create Date: 2023-10-13 17:08:21.656060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3809c8911d1'
down_revision: Union[str, None] = 'f8a81779db51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
