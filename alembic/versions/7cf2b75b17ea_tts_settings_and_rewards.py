"""tts_settings_and_rewards

Revision ID: 7cf2b75b17ea
Revises: cbec9fdeeeb7
Create Date: 2023-11-30 17:27:42.189969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cf2b75b17ea'
down_revision: Union[str, None] = 'cbec9fdeeeb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('tts_included', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('tts_nickname', sa.VARCHAR(length=20), nullable=True))
    with op.batch_alter_table('user') as bat:
        bat.alter_column(
            'platform_user_id',
            existing_type=sa.String(),
            nullable=False,
        )
    op.create_table(
        'reward',
        sa.Column('reward_id', sa.Integer, primary_key=True),
        sa.Column('platform_reward_id', sa.Uuid, unique=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('tts_name', sa.String, nullable=True, default=None),
    )


def downgrade() -> None:
    op.drop_table('reward')
    with op.batch_alter_table('user') as bat:
        bat.alter_column(
            'platform',
            existing_type=sa.VARCHAR(),
            nullable=True,
        )
        bat.drop_column('tts_nickname')
        bat.drop_column('tts_included')
