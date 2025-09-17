from pydantic import BaseModel, Field
from typing import Optional

class _ZAPITextPayload(BaseModel):
    message: str

class ZAPIPayload(BaseModel):
    phone: str
    message_type: str = Field(..., alias="type")
    text: Optional[_ZAPITextPayload] = None
    media_url: Optional[str] = Field(None, alias="mediaUrl")
    mime_type: Optional[str] = Field(None, alias="mimeType")