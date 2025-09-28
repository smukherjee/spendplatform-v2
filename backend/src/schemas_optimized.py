"""
Optimized Pydantic schemas with pagination support
"""
from pydantic import BaseModel, Field
from typing import List, Generic, TypeVar, Optional
from datetime import datetime

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    skip: int = Field(..., ge=0, description="Number of items skipped")
    limit: int = Field(..., ge=1, le=1000, description="Maximum items per page")
    has_next: bool = Field(..., description="Whether there are more items")

class UserReadOptimized(BaseModel):
    """Optimized user read schema"""
    id: int
    username: str
    email: str
    client_id: int
    personalisation: Optional[dict] = None
    roles: List[str] = []
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Type aliases for common paginated responses
PaginatedUserResponse = PaginatedResponse[UserReadOptimized]