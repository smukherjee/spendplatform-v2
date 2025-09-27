from pydantic import BaseModel
from typing import Optional, List

# Screen schemas
class ScreenBase(BaseModel):
    name: str
    route: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

class ScreenCreate(ScreenBase):
    pass

class ScreenRead(ScreenBase):
    id: int
    model_config = {"from_attributes": True}

# Role Screen Permission schemas
class RoleScreenPermissionBase(BaseModel):
    role_id: int
    screen_id: int
    client_id: int
    allow_access: bool = False

class RoleScreenPermissionCreate(RoleScreenPermissionBase):
    pass

class RoleScreenPermissionRead(RoleScreenPermissionBase):
    id: int
    model_config = {"from_attributes": True}

class RoleScreenPermissionWithDetails(RoleScreenPermissionRead):
    screen: Optional[ScreenRead] = None
    role_name: Optional[str] = None

# User Screen Permission schemas
class UserScreenPermissionBase(BaseModel):
    user_id: int
    screen_id: int
    allow_access: bool = False

class UserScreenPermissionCreate(UserScreenPermissionBase):
    pass

class UserScreenPermissionRead(UserScreenPermissionBase):
    id: int
    model_config = {"from_attributes": True}

class UserScreenPermissionWithDetails(UserScreenPermissionRead):
    screen: Optional[ScreenRead] = None
    username: Optional[str] = None

# Bulk permission update schemas
class BulkRolePermissionUpdate(BaseModel):
    role_id: int
    client_id: int
    permissions: List[dict]  # [{"screen_id": 1, "allow_access": true}, ...]

class BulkUserPermissionUpdate(BaseModel):
    user_id: int
    permissions: List[dict]  # [{"screen_id": 1, "allow_access": true}, ...]

# Permission check response
class PermissionCheckResponse(BaseModel):
    screen_route: str
    has_access: bool
    source: str  # "role", "user_override", "denied"
    message: Optional[str] = None