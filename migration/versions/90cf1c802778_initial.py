"""Initial

Revision ID: 90cf1c802778
Revises: 
Create Date: 2023-12-22 14:54:56.169929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90cf1c802778'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('permissions', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('firstname', sa.String(), nullable=True),
    sa.Column('lastname', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('registered_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('oauth_account',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('oauth_name', sa.String(), nullable=False),
    sa.Column('access_token', sa.String(), nullable=False),
    sa.Column('expires_at', sa.Integer(), nullable=True),
    sa.Column('refresh_token', sa.Integer(), nullable=True),
    sa.Column('account_id', sa.String(), nullable=False),
    sa.Column('account_email', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oauth_account_account_id'), 'oauth_account', ['account_id'], unique=False)
    op.create_index(op.f('ix_oauth_account_oauth_name'), 'oauth_account', ['oauth_name'], unique=False)
    op.create_table('wallet',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='NO ACTION', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('currency',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('wallet_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallet.id'], onupdate='NO ACTION', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('wallet_id', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=100), nullable=False),
    sa.Column('currency_2', sa.String(length=100), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('executed_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallet.id'], onupdate='NO ACTION', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    op.drop_table('currency')
    op.drop_table('wallet')
    op.drop_index(op.f('ix_oauth_account_oauth_name'), table_name='oauth_account')
    op.drop_index(op.f('ix_oauth_account_account_id'), table_name='oauth_account')
    op.drop_table('oauth_account')
    op.drop_table('user')
    op.drop_table('role')
    # ### end Alembic commands ###