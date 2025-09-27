from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.src.utils import verify_password, get_password_hash, create_access_token
from fastapi import FastAPI

app = FastAPI()

@app.post("/token", summary="OAuth2 login and JWT token generation")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
	# Dummy user store for demo; replace with DB lookup
	users = {
		"superadmin": {"username": "superadmin", "hashed_password": get_password_hash("superadminpw"), "role": "superadmin", "client_id": None},
		"clientadmin": {"username": "clientadmin", "hashed_password": get_password_hash("clientadminpw"), "role": "client_admin", "client_id": 1},
		"user": {"username": "user", "hashed_password": get_password_hash("userpw"), "role": "user", "client_id": 1},
	}
	user = users.get(form_data.username)
	if not user or not verify_password(form_data.password, user["hashed_password"]):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
	token_data = {"sub": user["username"], "role": user["role"], "client_id": user["client_id"]}
	access_token = create_access_token(token_data)
	return {"access_token": access_token, "token_type": "bearer"}
"""
FastAPI Endpoint Scaffolding
- All endpoints return 501 Not Implemented
- RBAC enforced via dummy JWT claims (to be replaced)
- Models and schemas are imported from backend/src/schemas
"""
from fastapi import FastAPI
from backend.src.routers.client import router as client_router
from backend.src.routers.user import router as user_router
from backend.src.routers.role import router as role_router
from backend.src.routers.business_unit import router as business_unit_router
from backend.src.routers.region import router as region_router
from backend.src.routers.supplier import router as supplier_router
from backend.src.routers.invoice import router as invoice_router
from backend.src.routers.invoice_item import router as invoice_item_router
from backend.src.routers.subcategory import router as subcategory_router
from backend.src.routers.unit_of_measure import router as unit_of_measure_router
from backend.src.routers.currency import router as currency_router
from backend.src.routers.client_settings import router as client_settings_router
from backend.src.routers.reporting import router as reporting_router
from backend.src.routers.audit import router as audit_router
from backend.src.utils import get_current_role, not_implemented

app = FastAPI()

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

