from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from schemas.client import ClientCreate, ClientRead
from models.client import Client
from database import get_db
from utils import get_current_role, enforce_role, get_client_id
from logging_config import log_audit

router = APIRouter(prefix="/clients", tags=["Client"])

@router.get("", response_model=List[ClientRead], summary="List all clients")
def get_clients(role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a list of all clients (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="get_clients", user=role, client_id=client_id, details="List clients")
    
    clients = db.query(Client).filter(Client.is_deleted == False).all()
    return clients

@router.post("", response_model=ClientRead, summary="Create a new client")
def post_clients(client: ClientCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Creates a new client (superladmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="post_clients", user=role, client_id=client_id, details=f"Create client: {client.name}")
    
    # Create new client
    db_client = Client(
        name=client.name,
        created_by=1  # TODO: Get actual user ID from JWT
    )
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client

@router.get("/{id}", response_model=ClientRead, summary="Get a client by ID")
def get_client(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Returns a specific client by ID (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="get_client", user=role, client_id=client_id, details=f"Get client {id}")
    
    client = db.query(Client).filter(
        Client.id == id,
        Client.is_deleted == False
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    return client

@router.put("/{id}", response_model=ClientRead, summary="Update a client")
def put_client(id: int, client: ClientCreate, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Updates a client by ID (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="put_client", user=role, client_id=client_id, details=f"Update client id: {id}")
    
    # Find existing client
    db_client = db.query(Client).filter(
        Client.id == id,
        Client.is_deleted == False
    ).first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update fields
    for field, value in client.dict().items():
        setattr(db_client, field, value)
    
    setattr(db_client, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    db.refresh(db_client)
    
    return db_client

@router.delete("/{id}", response_model=None, summary="Delete a client")
def delete_client(id: int, role: str = Depends(get_current_role), client_id: int = Depends(get_client_id), db: Session = Depends(get_db)):
    """Deletes a client by ID (superadmin only)."""
    enforce_role(role, ["superadmin"])
    log_audit(action="delete_client", user=role, client_id=client_id, details=f"Delete client id: {id}")
    
    # Find existing client
    db_client = db.query(Client).filter(
        Client.id == id,
        Client.is_deleted == False
    ).first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Soft delete
    setattr(db_client, "is_deleted", True)
    setattr(db_client, "updated_by", 1)  # TODO: Get actual user ID from JWT
    
    db.commit()
    
    return {"message": "Client deleted successfully"}
