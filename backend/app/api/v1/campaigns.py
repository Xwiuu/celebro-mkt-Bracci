from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import date
from typing import List, Optional

from app.db.session import get_db
from app.models.campaign import Campaign, CampaignInsight
from app.services.meta_service import sync_meta_campaigns

router = APIRouter()

@router.get("/")
async def list_campaigns(
    start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(2000),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista as campanhas somando os insights diários dentro do período escolhido.
    Lógica de Gerenciador de Anúncios Profissional.
    """
    try:
        # 1. Construímos a Query com Joins e Agrupamento
        # O segredo está no func.sum() e func.avg()
        query = (
            select(
                Campaign.id,
                Campaign.nome,
                Campaign.status,
                Campaign.plataforma,
                func.sum(CampaignInsight.spend).label("investimento_total"),
                func.sum(CampaignInsight.revenue).label("revenue"),
                func.sum(CampaignInsight.clicks).label("clicks"),
                func.sum(CampaignInsight.impressions).label("impressions"),
                # Média ponderada do ROAS e CTR no período
                func.avg(CampaignInsight.roas).label("roas"),
                func.avg(CampaignInsight.ctr).label("ctr"),
                func.avg(CampaignInsight.cpa).label("cpa")
            )
            .join(CampaignInsight, Campaign.id == CampaignInsight.campaign_id)
            .where(CampaignInsight.data >= start_date)
            .where(CampaignInsight.data <= end_date)
        )

        # 2. Filtros de Atividade e Plataforma
        if platform:
            query = query.where(Campaign.plataforma.ilike(f"%{platform}%"))
        
        if status:
            query = query.where(Campaign.status == status)

        # 3. Agrupamos por ID da campanha para somar os dias
        query = query.group_by(Campaign.id).limit(limit)

        result = await db.execute(query)
        # Transformamos em dicionários para o FastAPI entregar o JSON limpo
        rows = result.all()
        
        campaigns_list = []
        for r in rows:
            campaigns_list.append({
                "id": r.id,
                "nome": r.nome,
                "status": r.status,
                "plataforma": r.plataforma,
                "investimento_total": round(float(r.investimento_total or 0), 2),
                "revenue": round(float(r.revenue or 0), 2),
                "roas": round(float(r.roas or 0), 2),
                "ctr": round(float(r.ctr or 0), 4),
                "cpa": round(float(r.cpa or 0), 2),
                "clicks": int(r.clicks or 0),
                "impressions": int(r.impressions or 0)
            })

        return {"data": campaigns_list}

    except Exception as e:
        print(f"❌ ERRO NA ROTA DE CAMPANHAS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_total_summary(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o totalzão de todas as campanhas no período (Os números gigantes do Dash).
    """
    query = (
        select(
            func.sum(CampaignInsight.spend).label("total_spend"),
            func.sum(CampaignInsight.revenue).label("total_revenue")
        )
        .where(CampaignInsight.data >= start_date)
        .where(CampaignInsight.data <= end_date)
    )
    
    result = await db.execute(query)
    row = result.first()
    
    return {
        "total_spend": round(float(row.total_spend or 0), 2),
        "total_revenue": round(float(row.total_revenue or 0), 2)
    }