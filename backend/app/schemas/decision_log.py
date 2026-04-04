from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class DecisionLogBase(BaseModel):
    acao_sugerida: str
    justificativa_ia: str
    executado_pelo_gestor: bool = False

class DecisionLogCreate(DecisionLogBase):
    campaign_id: int

class DecisionLog(DecisionLogBase):
    id: int
    campaign_id: int
    data_decisao: datetime

    model_config = ConfigDict(from_attributes=True)
