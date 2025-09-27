from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models.subcategory import SubCategoryL1
from schemas.subcategory import SubCategoryCreate, SubCategoryRead
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/subcategories", tags=["SubCategory"])

@router.get("", response_model=List[SubCategoryRead], summary="List all subcategories")
def get_subcategories(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all subcategories for the current client (unless superadmin)."""
    log_audit(action="get_subcategories", user=role, client_id=client_id, details="List subcategories")
    
    if role == "superadmin":
        subcategories = db.query(SubCategoryL1).filter(SubCategoryL1.is_deleted == False).all()
    else:
        subcategories = db.query(SubCategoryL1).filter(
            SubCategoryL1.client_id == client_id,
            SubCategoryL1.is_deleted == False
        ).all()
    
    return subcategories

@router.post("", response_model=SubCategoryRead, summary="Create a new subcategory")
def post_subcategories(subcat: SubCategoryCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new subcategory for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_subcategories", user=role, client_id=client_id, details=f"Create subcategory: {subcat.name}")
    
    # Create new subcategory
    db_subcat = SubCategoryL1(
        name=subcat.name,
        description=getattr(subcat, 'description', None),
        client_id=client_id if role != "superadmin" else getattr(subcat, 'client_id', client_id),
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_subcat)
    db.commit()
    db.refresh(db_subcat)
    
    return db_subcat

@router.get("/{id}", response_model=SubCategoryRead, summary="Get a subcategory by ID")
def get_subcategory(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a subcategory by ID, filtered by client if not superadmin."""
    log_audit(action="get_subcategory", user=role, client_id=client_id, details=f"Get subcategory id: {id}")
    
    if role == "superadmin":
        subcat = db.query(SubCategoryL1).filter(
            SubCategoryL1.id == id,
            SubCategoryL1.is_deleted == False
        ).first()
    else:
        subcat = db.query(SubCategoryL1).filter(
            SubCategoryL1.id == id,
            SubCategoryL1.client_id == client_id,
            SubCategoryL1.is_deleted == False
        ).first()
    
    if not subcat:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    return subcat

@router.put("/{id}", response_model=SubCategoryRead, summary="Update a subcategory")
def put_subcategory(id: int, subcat: SubCategoryCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a subcategory by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_subcategory", user=role, client_id=client_id, details=f"Update subcategory id: {id}")
    
    # Find existing subcategory
    if role == "superadmin":
        db_subcat = db.query(SubCategoryL1).filter(
            SubCategoryL1.id == id,
            SubCategoryL1.is_deleted == False
        ).first()
    else:
        db_subcat = db.query(SubCategoryL1).filter(
            SubCategoryL1.id == id,
            SubCategoryL1.client_id == client_id,
            SubCategoryL1.is_deleted == False
        ).first()
    
    if not db_subcat:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    # Update fields
    for field, value in subcat.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_subcat, field, value)
    
    setattr(db_subcat, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_subcat)
    
    return db_subcat

@router.delete("/{id}", response_model=None, summary="Delete a subcategory")
def delete_subcategory(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a subcategory by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_subcategory", user=role, client_id=client_id, details=f"Delete subcategory id: {id}")
    
    # Find existing subcategory
    if role == "superadmin":
        db_subcat = db.query(SubCategoryL1).filter(
            SubCategoryL1.id == id,
            SubCategoryL1.is_deleted == False
        ).first()
    else:
        db_subcat = db.query(SubCategoryL1).filter(
            SubCategoryL1.id == id,
            SubCategoryL1.client_id == client_id,
            SubCategoryL1.is_deleted == False
        ).first()
    
    if not db_subcat:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    # Soft delete
    setattr(db_subcat, "is_deleted", True)
    setattr(db_subcat, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Subcategory deleted successfully"}
