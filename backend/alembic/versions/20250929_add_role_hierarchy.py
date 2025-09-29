"""Add hierarchy and client scoping to roles

Revision ID: add_role_hierarchy
Revises: drop_user_permissions
Create Date: 2025-09-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String

# revision identifiers, used by Alembic.
revision: str = 'add_role_hierarchy'
down_revision: Union[str, Sequence[str], None] = 'drop_user_permissions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add hierarchy metadata and client scoping to roles."""
    # Add new columns
    op.add_column('role', sa.Column('hierarchy_level', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('role', sa.Column('parent_role_id', sa.Integer(), nullable=True))
    op.add_column('role', sa.Column('client_id', sa.Integer(), nullable=True))

    # Create supporting indexes and constraints
    op.create_foreign_key('fk_role_parent_role', 'role', 'role', ['parent_role_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_role_client', 'role', 'client', ['client_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_role_hierarchy_level', 'role', ['hierarchy_level'])
    op.create_index('ix_role_client', 'role', ['client_id'])
    op.create_unique_constraint('uq_role_name_client', 'role', ['name', 'client_id'])

    # Populate hierarchy defaults for existing roles
    role_table = table(
        'role',
        column('id', Integer),
        column('name', String),
        column('hierarchy_level', Integer),
        column('client_id', Integer),
    )

    # Superadmin defaults to top hierarchy (0) and global scope
    op.execute(
        role_table.update()
        .where(role_table.c.name == 'superadmin')
        .values(hierarchy_level=0, client_id=None)
    )

    # Client admin defaults to next level (1)
    op.execute(
        role_table.update()
        .where(role_table.c.name == 'client_admin')
        .values(hierarchy_level=1)
    )

    # Any remaining roles default to level 2
    op.execute(
        role_table.update()
        .where(sa.and_(role_table.c.name != 'superadmin', role_table.c.name != 'client_admin'))
        .values(hierarchy_level=2)
    )

    # Remove server default now that data is populated
    op.alter_column('role', 'hierarchy_level', existing_type=sa.Integer(), server_default=None)


def downgrade() -> None:
    """Revert role hierarchy changes."""
    op.drop_constraint('uq_role_name_client', 'role', type_='unique')
    op.drop_index('ix_role_client', table_name='role')
    op.drop_index('ix_role_hierarchy_level', table_name='role')
    op.drop_constraint('fk_role_client', 'role', type_='foreignkey')
    op.drop_constraint('fk_role_parent_role', 'role', type_='foreignkey')
    op.drop_column('role', 'client_id')
    op.drop_column('role', 'parent_role_id')
    op.drop_column('role', 'hierarchy_level')
