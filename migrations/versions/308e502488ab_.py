"""empty message

Revision ID: 308e502488ab
Revises: c544f4ae9030
Create Date: 2025-04-12 11:04:48.077416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '308e502488ab'
down_revision: Union[str, None] = 'c544f4ae9030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE TYPE call_type AS ENUM ('CRITICAL', 'IMPORTANT', 'COMMON')")
    op.add_column('call', sa.Column('type', sa.Enum('CRITICAL', 'IMPORTANT', 'COMMON', name='call_type'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('call', 'type')
    op.execute("DROP TYPE IF EXISTS call_type")
    # ### end Alembic commands ###
