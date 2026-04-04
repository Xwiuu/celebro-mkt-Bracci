from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DecisionHubBase(BaseModel):
    tipo_acao: str
    impacto_estimado: float
    justificativa_neuro: str
    status: str = "pendente"

class DecisionHubCreate(DecisionHubBase):
    campaign_id: int

class DecisionHub(DecisionHubBase):
    id: int
    campaign_id: int
    data_proposta: datetime

    model_config = ConfigDict(from_attributes=True)
