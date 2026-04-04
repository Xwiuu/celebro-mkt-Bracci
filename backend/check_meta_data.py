import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.session import engine # <--- Esse cara o reset_db.py usa, então existe!
from app.models.campaign import CampaignInsight
from datetime import date

# Criamos a fábrica de sessão aqui mesmo para não ter erro de import
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def check_totals():
    async with AsyncSessionLocal() as db:
        # 1. Teste do Mês Inteiro (Março 2026)
        start_date = date(2026, 3, 1)
        end_date = date(2026, 3, 31)
        
        stmt_month = select(
            func.sum(CampaignInsight.spend).label("total_spend"),
            func.sum(CampaignInsight.impressions).label("total_impressions")
        ).where(CampaignInsight.data.between(start_date, end_date))
        
        res_month = await db.execute(stmt_month)
        totals = res_month.one()
        
        # 2. Teste dos últimos 2 dias (30/03 a 31/03)
        stmt_days = select(
            func.sum(CampaignInsight.spend).label("total_spend")
        ).where(CampaignInsight.data.between(date(2026, 3, 30), date(2026, 3, 31)))
        
        res_days = await db.execute(stmt_days)
        total_2_days = res_days.scalar()

        print("\n" + "="*50)
        print("📊 --- RELATÓRIO DE CONFERÊNCIA (MARÇO) ---")
        print("="*50)
        print(f"📅 Período: 01/03 a 31/03")
        print(f"💰 Gasto Total no Banco: R$ {totals.total_spend or 0:.2f}")
        print(f"👁️ Impressões Totais: {totals.total_impressions or 0}")
        print("-" * 40)
        print(f"📅 Período: 30/03 a 31/03")
        print(f"💰 Gasto Total no Banco: R$ {total_2_days or 0:.2f}")
        print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(check_totals())