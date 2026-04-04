from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class CreativeBase(BaseModel):
    url_imagem_video: str
    copy_text: str
    score_ia: float = Field(default=0.0, ge=0.0, le=10.0)

class CreativeCreate(CreativeBase):
    campaign_id: int

class CreativeUpdate(BaseModel):
    url_imagem_video: Optional[str] = None
    copy_text: Optional[str] = None
    score_ia: Optional[float] = Field(None, ge=0.0, le=10.0)

class Creative(CreativeBase):
    id: int
    campaign_id: int

    model_config = ConfigDict(from_attributes=True)
