from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    acao_sugerida: Mapped[str] = mapped_column(String(100))
    justificativa_ia: Mapped[str] = mapped_column(String)
    executado_pelo_gestor: Mapped[bool] = mapped_column(Boolean, default=False)
    data_decisao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign: Mapped["Campaign"] = relationship(back_populates="decision_logs")
