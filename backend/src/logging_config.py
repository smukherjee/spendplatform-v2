import logging
from logging.handlers import RotatingFileHandler
from models.audit import AuditLog
from sqlalchemy.orm import Session
import os

LOG_TO_CONSOLE = os.environ.get("LOG_TO_CONSOLE", "true").lower() == "true"
LOG_TO_FILE = os.environ.get("LOG_TO_FILE", "true").lower() == "true"
LOG_TO_DB = os.environ.get("LOG_TO_DB", "false").lower() == "true"
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "app.log")

logger = logging.getLogger("spendplatform")
logger.setLevel(logging.INFO)

if LOG_TO_CONSOLE:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

if LOG_TO_FILE:
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

from typing import Optional
def log_audit(action: str, user: str, client_id: Optional[int] = None, details: Optional[str] = None, db: Optional[Session] = None):
    msg = f"AUDIT: user={user}, client_id={client_id}, action={action}, details={details}"
    logger.info(msg)
    if LOG_TO_DB and db is not None:
        audit = AuditLog(user=user, client_id=client_id, action=action, details=details)
        db.add(audit)
        db.commit()
