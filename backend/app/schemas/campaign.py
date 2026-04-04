from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class CampaignBase(BaseModel):
    nome: str
    plataforma: str
    tipo_origem: str = "PAGO"
    status: str = "ativa"
    investimento_diario: float = 0.0
    investimento_total: float = 0.0
    ctr: float = 0.0
    cpa: float = 0.0
    roas: float = 0.0

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    nome: Optional[str] = None
    plataforma: Optional[str] = None
    status: Optional[str] = None
    investimento_diario: Optional[float] = None
    ctr: Optional[float] = None
    cpa: Optional[float] = None
    roas: Optional[float] = None

from app.schemas.decision_log import DecisionLog as DecisionLogSchema

class Campaign(CampaignBase):
    id: int
    data_criacao: datetime
    latest_decision: Optional[DecisionLogSchema] = None

    model_config = ConfigDict(from_attributes=True)
