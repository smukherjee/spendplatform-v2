from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models.unit_of_measure import UnitOfMeasure
from schemas.unit_of_measure import UnitOfMeasureCreate, UnitOfMeasureRead
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/unit-of-measures", tags=["UnitOfMeasure"])

@router.get("", response_model=List[UnitOfMeasureRead], summary="List all units of measure")
def get_units_of_measure(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all units of measure for the current client (unless superadmin)."""
    log_audit(action="get_units_of_measure", user=role, client_id=client_id, details="List units of measure")
    
    if role == "superadmin":
        units = db.query(UnitOfMeasure).filter(UnitOfMeasure.is_deleted == False).all()
    else:
        units = db.query(UnitOfMeasure).filter(
            UnitOfMeasure.client_id == client_id,
            UnitOfMeasure.is_deleted == False
        ).all()
    
    return units

@router.post("", response_model=UnitOfMeasureRead, summary="Create a new unit of measure")
def post_units_of_measure(uom: UnitOfMeasureCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new unit of measure for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_units_of_measure", user=role, client_id=client_id, details=f"Create unit of measure: {uom.name}")
    
    # Create new unit of measure
    db_uom = UnitOfMeasure(
        name=uom.name,
        abbreviation=getattr(uom, 'abbreviation', None),
        client_id=client_id if role != "superadmin" else getattr(uom, 'client_id', client_id),
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_uom)
    db.commit()
    db.refresh(db_uom)
    
    return db_uom

@router.get("/{id}", response_model=UnitOfMeasureRead, summary="Get a unit of measure by ID")
def get_unit_of_measure(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a unit of measure by ID, filtered by client if not superadmin."""
    log_audit(action="get_unit_of_measure", user=role, client_id=client_id, details=f"Get unit of measure id: {id}")
    
    if role == "superadmin":
        uom = db.query(UnitOfMeasure).filter(
            UnitOfMeasure.id == id,
            UnitOfMeasure.is_deleted == False
        ).first()
    else:
        uom = db.query(UnitOfMeasure).filter(
            UnitOfMeasure.id == id,
            UnitOfMeasure.client_id == client_id,
            UnitOfMeasure.is_deleted == False
        ).first()
    
    if not uom:
        raise HTTPException(status_code=404, detail="Unit of measure not found")
    
    return uom

@router.put("/{id}", response_model=UnitOfMeasureRead, summary="Update a unit of measure")
def put_unit_of_measure(id: int, uom: UnitOfMeasureCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a unit of measure by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_unit_of_measure", user=role, client_id=client_id, details=f"Update unit of measure id: {id}")
    
    # Find existing unit of measure
    if role == "superadmin":
        db_uom = db.query(UnitOfMeasure).filter(
            UnitOfMeasure.id == id,
            UnitOfMeasure.is_deleted == False
        ).first()
    else:
        db_uom = db.query(UnitOfMeasure).filter(
            UnitOfMeasure.id == id,
            UnitOfMeasure.client_id == client_id,
            UnitOfMeasure.is_deleted == False
        ).first()
    
    if not db_uom:
        raise HTTPException(status_code=404, detail="Unit of measure not found")
    
    # Update fields
    for field, value in uom.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_uom, field, value)
    
    setattr(db_uom, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_uom)
    
    return db_uom

@router.delete("/{id}", response_model=None, summary="Delete a unit of measure")
def delete_unit_of_measure(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a unit of measure by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_unit_of_measure", user=role, client_id=client_id, details=f"Delete unit of measure id: {id}")
    
    # Find existing unit of measure
    if role == "superadmin":
        db_uom = db.query(UnitOfMeasure).filter(
            UnitOfMeasure.id == id,
            UnitOfMeasure.is_deleted == False
        ).first()
    else:
        db_uom = db.query(UnitOfMeasure).filter(
            UnitOfMeasure.id == id,
            UnitOfMeasure.client_id == client_id,
            UnitOfMeasure.is_deleted == False
        ).first()
    
    if not db_uom:
        raise HTTPException(status_code=404, detail="Unit of measure not found")
    
    # Soft delete
    setattr(db_uom, "is_deleted", True)
    setattr(db_uom, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Unit of measure deleted successfully"}
