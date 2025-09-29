from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models.currency import Currency
from schemas.currency import CurrencyCreate, CurrencyRead
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/currencies", tags=["Currency"])

@router.get("", response_model=List[CurrencyRead], summary="List all currencies")
def get_currencies(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all currencies for the current client (unless superadmin)."""
    log_audit(action="get_currencies", user=role, client_id=client_id, details="List currencies")
    
    if role == "superadmin":
        currencies = db.query(Currency).filter(Currency.is_deleted == False).all()
    else:
        currencies = db.query(Currency).filter(
            Currency.client_id == client_id,
            Currency.is_deleted == False
        ).all()
    
    return currencies

@router.post("", response_model=CurrencyRead, summary="Create a new currency")
def post_currencies(currency: CurrencyCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new currency for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_currencies", user=role, client_id=client_id, details=f"Create currency: {currency.code}")
    
    # Create new currency
    db_currency = Currency(
        code=currency.code,
        name=currency.name,
        symbol=getattr(currency, 'symbol', None),
        client_id=client_id if role != "superadmin" else currency.client_id,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    
    return db_currency

@router.get("/{id}", response_model=CurrencyRead, summary="Get a currency by ID")
def get_currency(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a currency by ID, filtered by client if not superadmin."""
    log_audit(action="get_currency", user=role, client_id=client_id, details=f"Get currency id: {id}")
    
    if role == "superadmin":
        currency = db.query(Currency).filter(
            Currency.id == id,
            Currency.is_deleted == False
        ).first()
    else:
        currency = db.query(Currency).filter(
            Currency.id == id,
            Currency.client_id == client_id,
            Currency.is_deleted == False
        ).first()
    
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    return currency

@router.put("/{id}", response_model=CurrencyRead, summary="Update a currency")
def put_currency(id: int, currency: CurrencyCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a currency by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="put_currency", user=role, client_id=client_id, details=f"Update currency id: {id}")
    
    # Find existing currency
    if role == "superadmin":
        db_currency = db.query(Currency).filter(
            Currency.id == id,
            Currency.is_deleted == False
        ).first()
    else:
        db_currency = db.query(Currency).filter(
            Currency.id == id,
            Currency.client_id == client_id,
            Currency.is_deleted == False
        ).first()
    
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    # Update fields
    for field, value in currency.dict().items():
        if field == "client_id" and role != "superadmin":
            continue  # Don't allow client_id updates for non-superadmin
        setattr(db_currency, field, value)
    
    setattr(db_currency, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_currency)
    
    return db_currency

@router.delete("/{id}", response_model=None, summary="Delete a currency")
def delete_currency(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a currency by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_currency", user=role, client_id=client_id, details=f"Delete currency id: {id}")
    
    # Find existing currency
    if role == "superadmin":
        db_currency = db.query(Currency).filter(
            Currency.id == id,
            Currency.is_deleted == False
        ).first()
    else:
        db_currency = db.query(Currency).filter(
            Currency.id == id,
            Currency.client_id == client_id,
            Currency.is_deleted == False
        ).first()
    
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    # Soft delete
    setattr(db_currency, "is_deleted", True)
    setattr(db_currency, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Currency deleted successfully"}
