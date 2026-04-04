from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal, get_db # Nome corrigido aqui!
from app.models.campaign import CampaignInsight
from datetime import date
from typing import List, Dict

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(
    start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o resumo de métricas e os dados para o gráfico de linha (Time-Series).
    """
    # 1. Busca os TOTAIS do período
    stmt_totals = select(
        func.sum(CampaignInsight.spend).label("total_spend"),
        func.sum(CampaignInsight.revenue).label("total_revenue"),
        func.sum(CampaignInsight.impressions).label("total_impressions"),
        func.sum(CampaignInsight.clicks).label("total_clicks")
    ).where(CampaignInsight.data.between(start_date, end_date))
    
    res_totals = await db.execute(stmt_totals)
    totals = res_totals.one()

    # 2. Busca os dados fatiados por DIA (pro Gráfico de Linha do Dashboard)
    stmt_daily = select(
        CampaignInsight.data,
        func.sum(CampaignInsight.spend).label("daily_spend"),
        func.sum(CampaignInsight.revenue).label("daily_revenue")
    ).where(
        CampaignInsight.data.between(start_date, end_date)
    ).group_by(CampaignInsight.data).order_by(CampaignInsight.data)

    res_daily = await db.execute(stmt_daily)
    
    # Monta a lista formatada para o Chart.js / Recharts do Next.js
    chart_data = [
        {
            "date": row.data.strftime("%Y-%m-%d"),
            "spend": round(float(row.daily_spend or 0), 2),
            "revenue": round(float(row.daily_revenue or 0), 2)
        } 
        for row in res_daily.all()
    ]

    # Cálculos Finais de Performance
    t_spend = float(totals.total_spend or 0)
    t_revenue = float(totals.total_revenue or 0)
    t_roas = (t_revenue / t_spend) if t_spend > 0 else 0.0

    return {
        "summary": {
            "total_spend": round(t_spend, 2),
            "total_revenue": round(t_revenue, 2),
            "total_roas": round(t_roas, 2),
            "total_impressions": totals.total_impressions or 0,
            "total_clicks": totals.total_clicks or 0
        },
        "chart_data": chart_data
    }