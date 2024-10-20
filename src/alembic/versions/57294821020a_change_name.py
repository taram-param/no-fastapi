"""change name

Revision ID: 57294821020a
Revises: c07a3b510ccc
Create Date: 2024-07-24 21:12:28.273210

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '57294821020a'
down_revision: Union[str, None] = 'c07a3b510ccc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user__user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user__user'))
    )
    op.create_index(op.f('ix_user__user_id'), 'user__user', ['id'], unique=False)
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_users')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.drop_index(op.f('ix_user__user_id'), table_name='user__user')
    op.drop_table('user__user')
    # ### end Alembic commands ###
