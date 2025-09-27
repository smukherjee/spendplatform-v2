from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.currency import CurrencyCreate, CurrencyRead
from utils import get_current_role, not_implemented, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/currencies", tags=["Currency"])

@router.get("", response_model=List[CurrencyRead], summary="List all currencies")
def get_currencies(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a list of all currencies for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="get_currencies", user=role, client_id=client_id, details="List currencies")
    # Example: query = db.query(Currency).filter(Currency.client_id == client_id) if role != "superadmin" else db.query(Currency)
    not_implemented()

@router.post("", response_model=CurrencyRead, summary="Create a new currency")
def post_currencies(currency: CurrencyCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Creates a new currency for the current client (unless superadmin)."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="post_currencies", user=role, client_id=client_id, details=f"Create currency: {currency.name if hasattr(currency, 'name') else ''}")
    # Example: currency.client_id = client_id if role != "superadmin" else currency.client_id
    not_implemented()

@router.get("/{id}", response_model=CurrencyRead, summary="Get a currency by ID")
def get_currency(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Returns a currency by ID, filtered by client if not superadmin."""
    log_audit(action="get_currency", user=role, client_id=client_id, details=f"Get currency id: {id}")
    not_implemented()

@router.put("/{id}", response_model=CurrencyRead, summary="Update a currency")
def put_currency(id: int, currency: CurrencyCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Updates a currency by ID, filtered by client if not superadmin."""
    log_audit(action="put_currency", user=role, client_id=client_id, details=f"Update currency id: {id}")
    not_implemented()

@router.delete("/{id}", response_model=None, summary="Delete a currency")
def delete_currency(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id)):
    """Deletes a currency by ID, filtered by client if not superadmin."""
    enforce_role(role, ["client_admin", "superadmin"])
    log_audit(action="delete_currency", user=role, client_id=client_id, details=f"Delete currency id: {id}")
    not_implemented()
