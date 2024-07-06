"""Add a email confirmed

Revision ID: bdb9e35a1ff5
Revises: 7eed38520d4d
Create Date: 2024-06-28 22:26:21.117813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdb9e35a1ff5'
down_revision: Union[str, None] = '7eed38520d4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
