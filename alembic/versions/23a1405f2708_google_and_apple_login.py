"""Google and Apple Login

Revision ID: 23a1405f2708
Revises: 1
Create Date: 2024-06-14 23:16:26.891257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23a1405f2708'
down_revision: Union[str, None] = '1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('provider', sa.String(length=50), nullable=False, server_default='local'))
    op.add_column('users', sa.Column('provider_id', sa.String(length=255), nullable=True))
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('users', 'provider_id')
    op.drop_column('users', 'provider')
    # ### end Alembic commands ###