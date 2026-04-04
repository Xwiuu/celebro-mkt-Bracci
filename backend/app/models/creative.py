from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Creative(Base):
    __tablename__ = "creatives"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    url_imagem_video: Mapped[str] = mapped_column(String(500))
    copy_text: Mapped[str] = mapped_column(String)
    score_ia: Mapped[float] = mapped_column(Float, default=0.0)

    campaign: Mapped["Campaign"] = relationship(back_populates="creatives")
