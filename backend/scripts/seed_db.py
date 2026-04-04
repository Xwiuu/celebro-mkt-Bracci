import asyncio
import sys
import os

# Adiciona o diretório raiz ao sys.path para permitir importações do app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.campaign import Campaign
# Importar outros modelos para garantir que o SQLAlchemy os reconheça na criação
from app.models.creative import Creative
from app.models.decision_log import DecisionLog

async def seed_data():
    print("--- Iniciando Setup do Banco de Dados ---")
    
    # 1. Cria as tabelas se não existirem
    async with engine.begin() as conn:
        print("Verificando/Criando tabelas...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tabelas prontas.")

    # 2. Popula com dados realistas (Nicho: Luxo/Bracci)
    print("\nIniciando a sementeira de dados (Meta Ads)...")
    async with AsyncSessionLocal() as session:
        # Campanha RUIM (Dreno de Verba)
        bad_campaign = Campaign(
            nome="[PERFORMANCE] - Torneiras Cozinha - Remarketing - FB",
            plataforma="Meta",
            status="ativa",
            investimento_diario=150.0,
            ctr=0.45,
            cpa=85.0,
            roas=0.82
        )

        # Campanha MEDIANA (Estável)
        medium_campaign = Campaign(
            nome="[CONVERSÃO] - Misturadores Monocomando - Lookalike 1% - FB",
            plataforma="Meta",
            status="ativa",
            investimento_diario=300.0,
            ctr=1.2,
            cpa=42.0,
            roas=2.85
        )

        # Campanha EXCELENTE (Estrela do Tráfego)
        gold_campaign = Campaign(
            nome="[ESCALA] - Linha Rose Gold - Interesses Luxo/Decor - FB",
            plataforma="Meta",
            status="ativa",
            investimento_diario=500.0,
            ctr=2.8,
            cpa=18.0,
            roas=6.4
        )

        session.add_all([bad_campaign, medium_campaign, gold_campaign])
        
        try:
            await session.commit()
            print("Sucesso: 3 campanhas (Ruim, Média e Ouro) foram criadas.")
        except Exception as e:
            await session.rollback()
            print(f"Erro ao popular banco: {e}")

if __name__ == "__main__":
    asyncio.run(seed_data())
