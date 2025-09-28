"""Drop user_screen_permission table - keep only role-based permissions

Revision ID: drop_user_permissions
Revises: us7_audit_log
Create Date: 2025-09-28 12:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'drop_user_permissions'
down_revision: Union[str, Sequence[str], None] = 'us7_audit_log'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop user_screen_permission table and all its constraints."""
    # Drop the user_screen_permission table (CASCADE will handle foreign key constraints)
    op.drop_table('user_screen_permission')


def downgrade() -> None:
    """Recreate user_screen_permission table."""
    op.create_table('user_screen_permission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('screen_id', sa.Integer(), nullable=False),
        sa.Column('allow_access', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['screen_id'], ['screen.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )