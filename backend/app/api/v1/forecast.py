from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.campaign import Campaign
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/revenue-forecast")
async def get_revenue_forecast(db: AsyncSession = Depends(get_db)):
    """
    Motor de Previsão de Receita: Projeta os próximos 15 dias baseado na tendência atual.
    """
    # 1. Busca dados atuais das campanhas
    result = await db.execute(select(Campaign))
    campaigns = result.scalars().all()
    
    if not campaigns:
        return {"realized": [], "forecast": []}

    # 2. Simulação de histórico de 7 dias (para fins de protótipo estatístico)
    # Em produção, leríamos de uma tabela de métricas diárias.
    total_daily_spend = sum(c.investimento_diario for c in campaigns)
    avg_roas = sum(c.roas for c in campaigns) / len(campaigns) if campaigns else 0
    
    dates_realized = [(datetime.now() - timedelta(days=i)).strftime("%d/%m") for i in range(6, -1, -1)]
    # Simula variação de ROAS nos últimos 7 dias
    realized_revenue = [total_daily_spend * (avg_roas + np.random.uniform(-0.5, 0.5)) for _ in range(7)]
    
    # 3. Cálculo de Tendência (Pandas)
    df = pd.DataFrame({"revenue": realized_revenue})
    growth_rate = df["revenue"].pct_change().mean() if len(df) > 1 else 0.05
    if np.isnan(growth_rate): growth_rate = 0.02

    # 4. Projeção de 15 dias
    forecast_data = []
    last_val = realized_revenue[-1]
    dates_forecast = []
    
    # Adiciona o último dia realizado ao forecast para conectar as linhas no gráfico
    forecast_data.append(round(last_val, 2))
    dates_forecast.append(dates_realized[-1])

    for i in range(1, 16):
        next_date = (datetime.now() + timedelta(days=i)).strftime("%d/%m")
        next_val = last_val * (1 + growth_rate) ** i
        forecast_data.append(round(next_val, 2))
        dates_forecast.append(next_date)

    return {
        "labels": dates_realized + dates_forecast[1:],
        "realized": [round(v, 2) for v in realized_revenue],
        "forecast": [None] * 6 + forecast_data, # Alinhamento para o Chart.js
        "metrics": {
            "avg_roas": round(avg_roas, 2),
            "estimated_growth": f"{round(growth_rate * 100, 2)}%"
        }
    }

@router.get("/comparative")
async def get_comparative_data(
    start_date_1: str, end_date_1: str,
    start_date_2: str, end_date_2: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Motor Comparativo: Analisa dois períodos e retorna a variação (Δ%) das métricas.
    """
    # Em uma implementação real, faríamos queries SQL agregando por data.
    # Aqui simulamos a estrutura baseada nos períodos informados.
    
    def simulate_period_metrics(seed):
        np.random.seed(seed)
        revenue = np.random.uniform(50000, 150000)
        investment = np.random.uniform(10000, 30000)
        roas = revenue / investment
        cpa = investment / (revenue / 500) # Simula ticket médio de 500
        return {
            "revenue": round(revenue, 2),
            "investment": round(investment, 2),
            "roas": round(roas, 2),
            "cpa": round(cpa, 2)
        }

    # Hash simples das datas para manter consistência no mock
    seed1 = hash(start_date_1 + end_date_1) % 1000
    seed2 = hash(start_date_2 + end_date_2) % 1000
    
    period1 = simulate_period_metrics(seed1)
    period2 = simulate_period_metrics(seed2)

    def calculate_delta(v1, v2):
        if v1 == 0: return 0
        return round(((v2 - v1) / v1) * 100, 2)

    metrics_comparison = {}
    for key in period1.keys():
        metrics_comparison[key] = {
            "p1": period1[key],
            "p2": period2[key],
            "delta": calculate_delta(period1[key], period2[key])
        }

    return {
        "periods": {
            "p1": {"start": start_date_1, "end": end_date_1},
            "p2": {"start": start_date_2, "end": end_date_2}
        },
        "comparison": metrics_comparison,
        "chart_data": {
            "labels": ["Receita", "Investimento"],
            "datasets": [
                {"label": "Período 1", "data": [period1["revenue"], period1["investment"]]},
                {"label": "Período 2", "data": [period2["revenue"], period2["investment"]]}
            ]
        }
    }

@router.get("/yoy-analysis")
async def get_yoy_analysis(current_date: str = None, db: AsyncSession = Depends(get_db)):
    """
    Calcula automaticamente o comparativo Mês Atual vs Mesmo Mês Ano Passado.
    """
    if not current_date:
        current_date = datetime.now().strftime("%Y-%m-%d")
    
    dt = datetime.strptime(current_date, "%Y-%m-%d")
    last_year_dt = dt.replace(year=dt.year - 1)
    
    # Simulação de dados YoY por canal
    def get_mock_platform_data(seed_offset=0):
        np.random.seed(seed_offset)
        return {
            "meta": {"revenue": np.random.uniform(40000, 60000), "spend": np.random.uniform(8000, 12000)},
            "google": {"revenue": np.random.uniform(30000, 50000), "spend": np.random.uniform(5000, 9000)}
        }

    current_metrics = get_mock_platform_data(dt.month)
    last_year_metrics = get_mock_platform_data(dt.month + 100) # Offset para ano passado

    return {
        "current_period": dt.strftime("%B %Y"),
        "last_year_period": last_year_dt.strftime("%B %Y"),
        "platforms": {
            "meta": {
                "current": current_metrics["meta"],
                "last_year": last_year_metrics["meta"],
                "delta_revenue": round(((current_metrics["meta"]["revenue"] - last_year_metrics["meta"]["revenue"]) / last_year_metrics["meta"]["revenue"]) * 100, 2)
            },
            "google": {
                "current": current_metrics["google"],
                "last_year": last_year_metrics["google"],
                "delta_revenue": round(((current_metrics["google"]["revenue"] - last_year_metrics["google"]["revenue"]) / last_year_metrics["google"]["revenue"]) * 100, 2)
            }
        }
    }

@router.get("/platforms-share")
async def get_platforms_share():
    """Retorna o share de investimento e eficiência entre Meta e Google."""
    return {
        "investment_share": [
            {"name": "Meta Ads", "value": 65, "color": "#1877F2"},
            {"name": "Google Ads", "value": 35, "color": "#4285F4"}
        ],
        "efficiency": [
            {"name": "Meta Ads", "roas": 5.8, "cpa": 12.50},
            {"name": "Google Ads", "roas": 4.2, "cpa": 18.90}
        ]
    }
