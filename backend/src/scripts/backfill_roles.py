#!/usr/bin/env python3
"""Utility script to backfill role hierarchy metadata.

This ensures hierarchy_level, client_id, and parent_role_id are populated for
all existing roles. It should be safe to run multiple times.
"""

import logging
from typing import Dict, Optional, Set

from sqlalchemy.orm import Session, joinedload

from database import SessionLocal
from models.role import Role, get_default_hierarchy_level

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _infer_unique_client_id(role: Role) -> Optional[int]:
    """Infer a client_id from assigned users when role.client_id is missing."""
    inferred: Set[Optional[int]] = {
        getattr(user, "client_id", None)
        for user in getattr(role, "users", []) or []
        if getattr(user, "client_id", None) is not None
    }
    if len(inferred) == 1:
        return inferred.pop()
    return None


def backfill_roles() -> None:
    """Backfill hierarchy metadata for existing roles."""
    session: Session = SessionLocal()
    try:
        logger.info("Starting role hierarchy backfill...")

        roles = (
            session.query(Role)
            .options(joinedload(Role.users))
            .order_by(Role.id)
            .all()
        )

        if not roles:
            logger.info("No roles found. Nothing to update.")
            return

        superadmin_role: Optional[Role] = None
        client_admin_by_client: Dict[int, Role] = {}
        updates = 0

        # Pass 1: normalise hierarchy level, locate superadmin, infer client IDs for non-user roles
        for role in roles:
            name = (getattr(role, "name", "") or "").strip().lower()
            desired_level = get_default_hierarchy_level(name)
            current_level = getattr(role, "hierarchy_level", None)
            if current_level != desired_level:
                setattr(role, "hierarchy_level", desired_level)
                updates += 1

            if name == "superadmin":
                if getattr(role, "client_id", None) is not None:
                    setattr(role, "client_id", None)
                    updates += 1
                if getattr(role, "parent_role_id", None) is not None:
                    setattr(role, "parent_role_id", None)
                    updates += 1
                superadmin_role = role
                continue

            if getattr(role, "client_id", None) is None:
                inferred_client = _infer_unique_client_id(role)
                if inferred_client is not None:
                    setattr(role, "client_id", inferred_client)
                    updates += 1

            if name == "client_admin" and getattr(role, "client_id", None) is not None:
                client_id_value = int(getattr(role, "client_id"))
                client_admin_by_client[client_id_value] = role

        # Ensure client_admin roles have superadmin as parent once located
        if superadmin_role is not None:
            for client_id_value, role in client_admin_by_client.items():
                if getattr(role, "parent_role_id", None) != superadmin_role.id:
                    setattr(role, "parent_role_id", superadmin_role.id)
                    updates += 1
        else:
            logger.warning("No superadmin role found; client_admin parent relationships were not updated.")

        # Pass 2: user roles inherit from client_admin of the same client
        for role in roles:
            name = (getattr(role, "name", "") or "").strip().lower()
            if name != "user":
                continue

            if getattr(role, "client_id", None) is None:
                inferred_client = _infer_unique_client_id(role)
                if inferred_client is not None:
                    setattr(role, "client_id", inferred_client)
                    updates += 1

            client_id_value = getattr(role, "client_id", None)
            if client_id_value is None:
                continue

            parent_role = client_admin_by_client.get(int(client_id_value))
            if parent_role and getattr(role, "parent_role_id", None) != parent_role.id:
                setattr(role, "parent_role_id", parent_role.id)
                updates += 1

        if updates:
            session.commit()
            logger.info("Role hierarchy backfill complete. Updated %s role records.", updates)
        else:
            logger.info("Role hierarchy backfill complete. No changes required.")

    except Exception as exc:
        session.rollback()
        logger.exception("Role hierarchy backfill failed: %s", exc)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    backfill_roles()
