"""empty message

Revision ID: fe00b1a21774
Revises: 90cf1c802778
Create Date: 2023-12-23 14:59:06.743959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe00b1a21774'
down_revision: Union[str, None] = '90cf1c802778'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('currency_name_key', 'currency', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('currency_name_key', 'currency', ['name'])
    # ### end Alembic commands ###
