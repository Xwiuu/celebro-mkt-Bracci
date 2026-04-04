import asyncio
import sys
import os

# Adiciona o diretório atual ao path para encontrar o módulo 'app'
sys.path.append(os.getcwd())

from app.db.session import engine
from app.models.base import Base
# Importar todos os modelos para garantir que o SQLAlchemy os reconheça
from app.models.campaign import Campaign
from app.models.creative import Creative
from app.models.decision_log import DecisionLog

async def init_db():
    print("Iniciando conexão com o banco de dados...")
    async with engine.begin() as conn:
        print("Criando tabelas baseadas nos modelos...")
        await conn.run_sync(Base.metadata.create_all)
        print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    asyncio.run(init_db())
