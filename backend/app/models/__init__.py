from sqlalchemy.orm import declarative_base

# A Base mora aqui agora!
Base = declarative_base()

# Importa os modelos para que a Base conheça as tabelas
from app.models.campaign import Campaign, CampaignInsight
# Se tiver outros (como creatives), importa aqui também:
# from app.models.creative import Creative