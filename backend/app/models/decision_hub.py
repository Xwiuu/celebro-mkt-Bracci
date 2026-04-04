from sqlalchemy import String, Float, Boolean, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import datetime
import enum

class DecisionStatus(str, enum.Enum):
    PENDING = "pendente"
    APPROVED = "aprovado"
    REJECTED = "rejeitado"

class DecisionHub(Base):
    __tablename__ = "decision_hub"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    tipo_acao: Mapped[str] = mapped_column(String(100)) # Escalar, Pausar, Criar Público, etc.
    status: Mapped[DecisionStatus] = mapped_column(String(20), default=DecisionStatus.PENDING)
    impacto_estimado: Mapped[float] = mapped_column(Float, default=0.0)
    justificativa_neuro: Mapped[str] = mapped_column(String)
    data_proposta: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign: Mapped["Campaign"] = relationship()
