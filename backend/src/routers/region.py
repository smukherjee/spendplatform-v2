from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.region import RegionCreate, RegionRead
from models.region import Region
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/regions", tags=["Region"])

@router.get("", response_model=List[RegionRead], summary="List all regions")
def get_regions(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all regions for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "user", "superadmin"])
    log_audit(action="get_regions", user=role, client_id=client_id, details="List regions")
    
    # Query regions based on role
    if role == "superadmin":
        regions = db.query(Region).filter(Region.is_deleted == False).all()
    else:
        regions = db.query(Region).filter(
            Region.client_id == client_id,
            Region.is_deleted == False
        ).all()
    
    return regions

@router.post("", response_model=RegionRead, summary="Create a new region")
def post_regions(region: RegionCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new region for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_regions", user=role, client_id=client_id, details=f"Create region: {region.name}")
    
    # Create new region
    db_region = Region(
        name=region.name,
        code=region.code,
        client_id=client_id if role != "superadmin" else region.client_id,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    
    return db_region

@router.get("/{id}", response_model=RegionRead, summary="Get a region by ID")
def get_region(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a region by ID, filtered by client if not superadmin."""
    log_audit(action="get_region", user=role, client_id=client_id, details=f"Get region id: {id}")
    
    # Query region based on role
    if role == "superadmin":
        region = db.query(Region).filter(
            Region.id == id,
            Region.is_deleted == False
        ).first()
    else:
        region = db.query(Region).filter(
            Region.id == id,
            Region.client_id == client_id,
            Region.is_deleted == False
        ).first()
    
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    return region

@router.put("/{id}", response_model=RegionRead, summary="Update a region")
def put_region(id: int, region: RegionCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a region by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_region", user=role, client_id=client_id, details=f"Update region id: {id}")
    
    # Find existing region
    if role == "superadmin":
        db_region = db.query(Region).filter(
            Region.id == id,
            Region.is_deleted == False
        ).first()
    else:
        db_region = db.query(Region).filter(
            Region.id == id,
            Region.client_id == client_id,
            Region.is_deleted == False
        ).first()
    
    if not db_region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Update fields
    for field, value in region.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_region, field, value)
    
    setattr(db_region, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_region)
    
    return db_region

@router.delete("/{id}", response_model=None, summary="Delete a region")
def delete_region(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a region by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_region", user=role, client_id=client_id, details=f"Delete region id: {id}")
    
    # Find existing region
    if role == "superadmin":
        db_region = db.query(Region).filter(
            Region.id == id,
            Region.is_deleted == False
        ).first()
    else:
        db_region = db.query(Region).filter(
            Region.id == id,
            Region.client_id == client_id,
            Region.is_deleted == False
        ).first()
    
    if not db_region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Soft delete
    setattr(db_region, "is_deleted", True)
    setattr(db_region, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Region deleted successfully"}
