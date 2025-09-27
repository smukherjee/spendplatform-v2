from pydantic import BaseModel
from typing import Optional

class ClientSettingsBase(BaseModel):
    client_id: int
    feature_flags: Optional[dict] = None
    branding: Optional[dict] = None
    ui_personalisation: Optional[dict] = None

class ClientSettingsCreate(ClientSettingsBase):
    pass

class ClientSettingsRead(ClientSettingsBase):
    id: int
    class Config:
        orm_mode = True
