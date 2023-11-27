"""update user

Revision ID: cbec9fdeeeb7
Revises: 1bd8499e2708
Create Date: 2023-11-26 16:23:55.344337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from twitch_bot.models.user import User


# revision identifiers, used by Alembic.
revision: str = 'cbec9fdeeeb7'
down_revision: Union[str, None] = '1bd8499e2708'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('platform', sa.String(), nullable=True),
        sa.Column('platform_user_id', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
    )
    with op.batch_alter_table('user') as bat:
        bat.create_unique_constraint('user_unique_name_platform', ['name', 'platform'])


def downgrade() -> None:
    op.drop_table('users')
