from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.business_unit import BusinessUnitCreate, BusinessUnitRead
from models.business_unit import BusinessUnit
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/business-units", tags=["BusinessUnit"])

@router.get("", response_model=List[BusinessUnitRead], summary="List all business units")
def get_business_units(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all business units for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "user", "superadmin"])
    log_audit(action="get_business_units", user=role, client_id=client_id, details="List business units")
    
    # Query business units based on role
    if role == "superadmin":
        business_units = db.query(BusinessUnit).filter(BusinessUnit.is_deleted == False).all()
    else:
        business_units = db.query(BusinessUnit).filter(
            BusinessUnit.client_id == client_id,
            BusinessUnit.is_deleted == False
        ).all()
    
    return business_units

@router.post("", response_model=BusinessUnitRead, summary="Create a new business unit")
def post_business_units(bu: BusinessUnitCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new business unit for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_business_units", user=role, client_id=client_id, details=f"Create business unit: {bu.name}")
    
    # Create new business unit
    db_bu = BusinessUnit(
        name=bu.name,
        code=bu.code,
        client_id=client_id if role != "superadmin" else bu.client_id,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_bu)
    db.commit()
    db.refresh(db_bu)
    
    return db_bu

@router.get("/{id}", response_model=BusinessUnitRead, summary="Get a business unit by ID")
def get_business_unit(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a business unit by ID, filtered by client if not superadmin."""
    log_audit(action="get_business_unit", user=role, client_id=client_id, details=f"Get business unit id: {id}")
    
    # Query business unit based on role
    if role == "superadmin":
        bu = db.query(BusinessUnit).filter(
            BusinessUnit.id == id,
            BusinessUnit.is_deleted == False
        ).first()
    else:
        bu = db.query(BusinessUnit).filter(
            BusinessUnit.id == id,
            BusinessUnit.client_id == client_id,
            BusinessUnit.is_deleted == False
        ).first()
    
    if not bu:
        raise HTTPException(status_code=404, detail="Business unit not found")
    
    return bu

@router.put("/{id}", response_model=BusinessUnitRead, summary="Update a business unit")
def put_business_unit(id: int, bu: BusinessUnitCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a business unit by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_business_unit", user=role, client_id=client_id, details=f"Update business unit id: {id}")
    
    # Find existing business unit
    if role == "superadmin":
        db_bu = db.query(BusinessUnit).filter(
            BusinessUnit.id == id,
            BusinessUnit.is_deleted == False
        ).first()
    else:
        db_bu = db.query(BusinessUnit).filter(
            BusinessUnit.id == id,
            BusinessUnit.client_id == client_id,
            BusinessUnit.is_deleted == False
        ).first()
    
    if not db_bu:
        raise HTTPException(status_code=404, detail="Business unit not found")
    
    # Update fields
    for field, value in bu.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_bu, field, value)
    
    setattr(db_bu, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_bu)
    
    return db_bu

@router.delete("/{id}", response_model=None, summary="Delete a business unit")
def delete_business_unit(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a business unit by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_business_unit", user=role, client_id=client_id, details=f"Delete business unit id: {id}")
    
    # Find existing business unit
    if role == "superadmin":
        db_bu = db.query(BusinessUnit).filter(
            BusinessUnit.id == id,
            BusinessUnit.is_deleted == False
        ).first()
    else:
        db_bu = db.query(BusinessUnit).filter(
            BusinessUnit.id == id,
            BusinessUnit.client_id == client_id,
            BusinessUnit.is_deleted == False
        ).first()
    
    if not db_bu:
        raise HTTPException(status_code=404, detail="Business unit not found")
    
    # Soft delete
    setattr(db_bu, "is_deleted", True)
    setattr(db_bu, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Business unit deleted successfully"}
