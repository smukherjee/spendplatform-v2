from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.client_settings import ClientSettings
from schemas.client_settings import ClientSettingsCreate, ClientSettingsRead
from utils import get_current_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/settings", tags=["ClientSettings"])

@router.get("", summary="Get client settings")
def get_settings(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns client settings for the current client (unless superadmin)."""
    log_audit(action="get_settings", user=role, client_id=client_id, details="Get client settings")
    
    if role == "superadmin":
        settings = db.query(ClientSettings).all()
    else:
        settings = db.query(ClientSettings).filter(ClientSettings.client_id == client_id).all()
    
    if not settings:
        # Return default settings array if none exist
        return [{
            "id": 0,
            "client_id": client_id,
            "feature_flags": {},
            "branding": {},
            "ui_personalisation": {}
        }]
    
    return [{"id": s.id, "client_id": s.client_id, "feature_flags": s.feature_flags or {}, "branding": s.branding or {}, "ui_personalisation": s.ui_personalisation or {}} for s in settings]

@router.put("", response_model=ClientSettingsRead, summary="Update client settings")
def put_settings(settings: ClientSettingsCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates client settings for the current client (unless superadmin)."""
    log_audit(action="put_settings", user=role, client_id=client_id, details="Update client settings")
    
    # Find existing settings
    db_settings = db.query(ClientSettings).filter(ClientSettings.client_id == client_id).first()
    
    if not db_settings:
        # Create new settings if none exist
        db_settings = ClientSettings(
            client_id=client_id,
            feature_flags=settings.feature_flags if hasattr(settings, 'feature_flags') else {},
            branding=settings.branding if hasattr(settings, 'branding') else {},
            ui_personalisation=settings.ui_personalisation if hasattr(settings, 'ui_personalisation') else {}
        )
        db.add(db_settings)
    else:
        # Update existing settings
        if hasattr(settings, 'feature_flags'):
            setattr(db_settings, 'feature_flags', settings.feature_flags)
        if hasattr(settings, 'branding'):
            setattr(db_settings, 'branding', settings.branding)
        if hasattr(settings, 'ui_personalisation'):
            setattr(db_settings, 'ui_personalisation', settings.ui_personalisation)
    
    db.commit()
    db.refresh(db_settings)
    
    return db_settings
