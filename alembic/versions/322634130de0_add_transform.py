"""'add_transform'

Revision ID: 322634130de0
Revises: 22ddadd022a9
Create Date: 2023-10-17 12:19:59.430914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '322634130de0'
down_revision: Union[str, None] = '22ddadd022a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photos', sa.Column('image_transform', sa.String(length=200), nullable=True))
    op.add_column('photos', sa.Column('qr_transform', sa.String(length=200), nullable=True))
    op.add_column('photos', sa.Column('public_id', sa.String(length=100), nullable=True))
    op.drop_constraint('photos_user_id_fkey', 'photos', type_='foreignkey')
    op.create_foreign_key(None, 'photos', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'photos', type_='foreignkey')
    op.create_foreign_key('photos_user_id_fkey', 'photos', 'users', ['user_id'], ['id'])
    op.drop_column('photos', 'public_id')
    op.drop_column('photos', 'qr_transform')
    op.drop_column('photos', 'image_transform')
    # ### end Alembic commands ###