from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

# Definimos a Base aqui para garantir que os modelos fiquem unidos
Base = declarative_base()

class Campaign(Base):
    """
    Tabela de Campanhas (O Chassi). 
    Unificada para Meta e Google Ads.
    """
    __tablename__ = "fb_campaigns"

    id = Column(String, primary_key=True, index=True) # ID da Plataforma (Varchar)
    nome = Column(String, nullable=False)
    
    # Identifica se é Meta ou Google no nível da campanha
    plataforma = Column(String, default="Meta") 
    
    tipo_origem = Column(String, default="PAGO")
    status = Column(String) # ACTIVE, PAUSED, ENABLED, etc.
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamento 1:N com os insights diários
    insights = relationship("CampaignInsight", back_populates="campaign", cascade="all, delete-orphan")

class CampaignInsight(Base):
    """
    Tabela de métricas diárias (Time-Series).
    Armazena o desempenho de cada campanha, dia após dia.
    """
    __tablename__ = "fb_campaign_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("fb_campaigns.id", ondelete="CASCADE"), index=True)
    data = Column(Date, index=True, nullable=False) # O dia do registro

    # 🚀 O PULO DO GATO: Adicionamos plataforma aqui para facilitar queries de soma
    platform = Column(String, default="meta") 

    # Métricas Financeiras
    spend = Column(Float, default=0.0) 
    revenue = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    
    # Métricas de Engajamento
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)

    campaign = relationship("Campaign", back_populates="insights")