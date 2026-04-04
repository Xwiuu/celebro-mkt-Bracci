from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, cast, String
from app.db.session import get_db
from app.models.campaign import Campaign, CampaignInsight
from app.core.redis import cache_service
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    """
    Retorna a inteligência completa: KPIs, Ranking e Gráficos.
    """
    # 1. CRIAR UMA CHAVE ÚNICA PARA ESSE FILTRO
    cache_key = f"dash:summary:{start_date}:{end_date}"

    # 2. TENTAR PEGAR DO REDIS
    cached_data = cache_service.get_cache(cache_key)
    if cached_data:
        return cached_data

    # --- SE NÃO TIVER NO CACHE, FAZ A QUERY NO BANCO ---
    try:
        # 1. KPIs GLOBAIS (Soma total das duas plataformas)
        total_query = select(
            func.sum(CampaignInsight.spend).label("total_spend"),
            func.sum(CampaignInsight.revenue).label("total_revenue"),
            func.sum(CampaignInsight.clicks).label("total_clicks"),
            func.sum(CampaignInsight.impressions).label("total_impressions")
        )
        res_total = await db.execute(total_query)
        totals = res_total.one()

        t_spend = float(totals.total_spend or 0)
        t_rev = float(totals.total_revenue or 0)
        t_clicks = int(totals.total_clicks or 0)
        t_impr = int(totals.total_impressions or 0)
        
        global_roas = (t_rev / t_spend) if t_spend > 0 else 0

        # 2. RANKING DE CAMPANHAS (Top 10 por Faturamento)
        # Unimos os Insights com a tabela de Campanhas para pegar o Nome e a Logo (Plataforma)
        ranking_query = (
            select(
                Campaign.nome,
                Campaign.plataforma,
                func.sum(CampaignInsight.spend).label("c_spend"),
                func.sum(CampaignInsight.revenue).label("c_revenue")
            )
            .join(Campaign, cast(Campaign.id, String) == CampaignInsight.campaign_id)
            .group_by(Campaign.id, Campaign.nome, Campaign.plataforma)
            .order_by(desc("c_revenue"))
            .limit(10)
        )
        res_ranking = await db.execute(ranking_query)
        ranking_data = []
        
        for r in res_ranking:
            s = float(r.c_spend or 0)
            rev = float(r.c_revenue or 0)
            ranking_data.append({
                "name": r.nome,
                "platform": r.plataforma.lower(), # 'meta' ou 'google'
                "spend": round(s, 2),
                "revenue": round(rev, 2),
                "roas": round(rev / s, 2) if s > 0 else 0
            })

        # 3. DADOS DO GRÁFICO (Evolução Diária por Plataforma)
        # Se não enviarem datas, usa os últimos 30 dias
        if start_date:
            date_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            date_start = datetime.now().date() - timedelta(days=30)
        
        if end_date:
            date_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            date_end = datetime.now().date()
        
        chart_query = (
            select(
                CampaignInsight.data,
                CampaignInsight.platform,
                func.sum(CampaignInsight.spend).label("daily_spend")
            )
            .where(CampaignInsight.data >= date_start)
            .where(CampaignInsight.data <= date_end)
            .group_by(CampaignInsight.data, CampaignInsight.platform)
            .order_by(CampaignInsight.data)
        )
        res_chart = await db.execute(chart_query)
        
        # Formata para o Front: { "2026-04-01": {"meta": 450.5, "google": 120.0}, ... }
        history = {}
        for r in res_chart:
            d_str = r.data.strftime("%Y-%m-%d")
            if d_str not in history:
                history[d_str] = {"meta": 0, "google": 0}
            
            # 🚨 O AJUSTE: Garante que pegue qualquer variação de nome (Google, google, GOOGLE)
            p_name = r.platform.lower()
            if "meta" in p_name or "facebook" in p_name:
                history[d_str]["meta"] += round(float(r.daily_spend or 0), 2)
            elif "google" in p_name:
                history[d_str]["google"] += round(float(r.daily_spend or 0), 2)

        response_data = {
            "success": True,
            "kpis": {
                "spend": round(t_spend, 2),
                "revenue": round(t_rev, 2),
                "roas": round(global_roas, 2),
                "clicks": t_clicks,
                "impressions": t_impr
            },
            "ranking": ranking_data,
            "chart_series": history
        }

        # 3. SALVAR NO REDIS ANTES DE RETORNAR
        # Expira em 1 hora pra garantir que os dados não fiquem velhos demais
        cache_service.set_cache(cache_key, response_data, expire_seconds=3600)

        return response_data

    except Exception as e:
        print(f"❌ Erro ao gerar Dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno no Dashboard: {str(e)}")


@router.get("/comparative")
async def get_comparative_data(
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """
    Comparação de períodos:
    - Período Atual: start_date até end_date
    - Período Anterior: mesma duração antes do start_date
    
    Retorna deltas (%) para cada métrica.
    """
    try:
        # 1. CONVERTE DATAS E CALCULA PERÍODOS
        s1 = datetime.strptime(start_date, "%Y-%m-%d").date()
        e1 = datetime.strptime(end_date, "%Y-%m-%d").date()
        diff = e1 - s1  # Diferença em dias

        # 2. PERÍODO ANTERIOR EQUIVALENTE
        e2 = s1 - timedelta(days=1)
        s2 = e2 - diff

        # 3. FUNÇÃO AUXILIAR PARA BUSCAR TOTAIS EM UM PERÍODO
        async def get_period_totals(start, end):
            """Busca spend e revenue total no período."""
            q = select(
                func.sum(CampaignInsight.spend).label("spend"),
                func.sum(CampaignInsight.revenue).label("revenue")
            ).where(CampaignInsight.data.between(start, end))
            
            res = await db.execute(q)
            row = res.one()
            return {
                "spend": float(row.spend or 0),
                "revenue": float(row.revenue or 0)
            }

        # 4. BUSCA DADOS ATUAL E ANTERIOR
        current_data = await get_period_totals(s1, e1)
        previous_data = await get_period_totals(s2, e2)

        # 5. CALCULA DELTAS (%)
        def calc_delta(current, previous):
            """Calcula mudança percentual."""
            if not previous or previous == 0:
                return 100.0 if current > 0 else 0.0
            return round(((current - previous) / previous) * 100, 2)

        # 6. MONTA RESPOSTA COM COMPARAÇÃO
        response_data = {
            "comparison": {
                "Faturamento": {
                    "current": current_data["revenue"],
                    "previous": previous_data["revenue"],
                    "delta": calc_delta(current_data["revenue"], previous_data["revenue"])
                },
                "Investimento": {
                    "current": current_data["spend"],
                    "previous": previous_data["spend"],
                    "delta": calc_delta(current_data["spend"], previous_data["spend"])
                },
                "ROAS": {
                    "current": current_data["revenue"] / current_data["spend"] if current_data["spend"] > 0 else 0,
                    "previous": previous_data["revenue"] / previous_data["spend"] if previous_data["spend"] > 0 else 0,
                    "delta": calc_delta(
                        current_data["revenue"] / current_data["spend"] if current_data["spend"] > 0 else 0,
                        previous_data["revenue"] / previous_data["spend"] if previous_data["spend"] > 0 else 0
                    )
                }
            }
        }

        # 7. SALVAR NO REDIS POR 1 HORA
        cache_key = f"dash:comparative:{start_date}:{end_date}"
        cache_service.set_cache(cache_key, response_data, expire_seconds=3600)

        print(f"📊 Comparação gerada: {s2.strftime('%Y-%m-%d')} a {e2.strftime('%Y-%m-%d')} vs {s1.strftime('%Y-%m-%d')} a {e1.strftime('%Y-%m-%d')}")

        return response_data

    except Exception as e:
        print(f"❌ Erro ao gerar Comparação: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na comparação: {str(e)}")