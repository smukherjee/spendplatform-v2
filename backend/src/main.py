
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from utils import verify_password, get_password_hash, create_access_token, get_current_role, not_implemented
from fastapi import FastAPI
from database import get_db
# Import all models to ensure relationships are initialized
from models.user import User
from models.role import Role
from models.user_role import user_role
from models.client import Client
from routers.client import router as client_router
from routers.user import router as user_router
from routers.role import router as role_router
from routers.business_unit import router as business_unit_router
from routers.region import router as region_router
from routers.supplier import router as supplier_router
from routers.invoice import router as invoice_router
from routers.invoice_item import router as invoice_item_router
from routers.subcategory import router as subcategory_router
from routers.unit_of_measure import router as unit_of_measure_router
from routers.currency import router as currency_router
from routers.client_settings import router as client_settings_router
from routers.reporting import router as reporting_router
from routers.audit import router as audit_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(client_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(business_unit_router)
app.include_router(region_router)
app.include_router(supplier_router)
app.include_router(invoice_router)
app.include_router(invoice_item_router)
app.include_router(subcategory_router)
app.include_router(unit_of_measure_router)
app.include_router(currency_router)
app.include_router(client_settings_router)
app.include_router(reporting_router)
app.include_router(audit_router)

# Register /token route on the correct app instance
@app.post("/token", summary="OAuth2 login and JWT token generation")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	# Database user lookup
	user = db.query(User).filter(User.username == form_data.username).first()
	if not user or not user.verify_password(form_data.password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
	
	# Simple role mapping based on username for now (until relationships are fixed)
	role_mapping = {
		"superadmin": "superadmin",
		"clientadmin": "client_admin", 
		"user": "user"
	}
	user_role = role_mapping.get(str(user.username), "user")
	
	token_data = {
		"sub": user.username,
		"role": user_role,
		"client_id": user.client_id,
		"user_id": user.id
	}
	access_token = create_access_token(token_data)
	return {"access_token": access_token, "token_type": "bearer"}

