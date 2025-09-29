from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models.import_error import ImportError
from schemas.import_error import ImportErrorCreate, ImportErrorRead
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/import-errors", tags=["ImportErrors"])

@router.get("", response_model=List[ImportErrorRead], summary="List all import errors")
def get_import_errors(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all import errors for the current client (unless superadmin)."""
    log_audit(action="get_import_errors", user=role, client_id=client_id, details="List import errors")
    
    if role == "superadmin":
        import_errors = db.query(ImportError).filter(ImportError.is_deleted == False).all()
    else:
        import_errors = db.query(ImportError).filter(
            ImportError.client_id == client_id,
            ImportError.is_deleted == False
        ).all()
    
    return import_errors

@router.post("", response_model=ImportErrorRead, summary="Create a new import error")
def create_import_error(import_error: ImportErrorCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new import error for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="create_import_error", user=role, client_id=client_id, details=f"Create import error: {import_error.error_message}")
    
    # Create new import error
    db_import_error = ImportError(
        invoice_id=import_error.invoice_id if hasattr(import_error, 'invoice_id') else None,
        row_number=import_error.row_number if hasattr(import_error, 'row_number') else None,
        error_type=import_error.error_type,
        error_message=import_error.error_message,
        error_details=import_error.error_details if hasattr(import_error, 'error_details') else None,
        resolved=import_error.resolved if hasattr(import_error, 'resolved') else False,
        client_id=client_id if role != "superadmin" else import_error.client_id,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_import_error)
    db.commit()
    db.refresh(db_import_error)
    return db_import_error

@router.get("/{id}", response_model=ImportErrorRead, summary="Get an import error by ID")
def get_import_error(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns an import error by ID, filtered by client if not superadmin."""
    log_audit(action="get_import_error", user=role, client_id=client_id, details=f"Get import error id: {id}")
    
    if role == "superadmin":
        import_error = db.query(ImportError).filter(
            ImportError.id == id,
            ImportError.is_deleted == False
        ).first()
    else:
        import_error = db.query(ImportError).filter(
            ImportError.id == id,
            ImportError.client_id == client_id,
            ImportError.is_deleted == False
        ).first()
    
    if not import_error:
        raise HTTPException(status_code=404, detail="Import error not found")
    return import_error

@router.put("/{id}", response_model=ImportErrorRead, summary="Update an import error")
def update_import_error(id: int, import_error: ImportErrorCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates an import error by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="update_import_error", user=role, client_id=client_id, details=f"Update import error id: {id}")
    
    if role == "superadmin":
        db_import_error = db.query(ImportError).filter(
            ImportError.id == id,
            ImportError.is_deleted == False
        ).first()
    else:
        db_import_error = db.query(ImportError).filter(
            ImportError.id == id,
            ImportError.client_id == client_id,
            ImportError.is_deleted == False
        ).first()
    
    if not db_import_error:
        raise HTTPException(status_code=404, detail="Import error not found")
    
    # Update fields
    for field, value in import_error.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_import_error, field, value)
    
    setattr(db_import_error, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_import_error)
    return db_import_error

@router.delete("/{id}", response_model=None, summary="Delete an import error")
def delete_import_error(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes an import error by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_import_error", user=role, client_id=client_id, details=f"Delete import error id: {id}")
    
    if role == "superadmin":
        db_import_error = db.query(ImportError).filter(
            ImportError.id == id,
            ImportError.is_deleted == False
        ).first()
    else:
        db_import_error = db.query(ImportError).filter(
            ImportError.id == id,
            ImportError.client_id == client_id,
            ImportError.is_deleted == False
        ).first()
    
    if not db_import_error:
        raise HTTPException(status_code=404, detail="Import error not found")
    
    # Soft delete
    setattr(db_import_error, "is_deleted", True)
    setattr(db_import_error, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Import error deleted successfully"}