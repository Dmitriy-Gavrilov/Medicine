"""empty message

Revision ID: 265bb360dce2
Revises: 1804aadfeca7
Create Date: 2025-04-07 17:56:53.500314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '265bb360dce2'
down_revision: Union[str, None] = '1804aadfeca7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('call', sa.Column('lat', sa.Float(), nullable=False))
    op.add_column('call', sa.Column('lon', sa.Float(), nullable=False))
    op.drop_column('call', 'coordinates')
    op.add_column('team', sa.Column('lat', sa.Float(), nullable=False))
    op.add_column('team', sa.Column('lon', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('team', 'lon')
    op.drop_column('team', 'lat')
    op.add_column('call', sa.Column('coordinates', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.drop_column('call', 'lon')
    op.drop_column('call', 'lat')
    # ### end Alembic commands ###
