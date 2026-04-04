from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.campaign import CampaignInsight
from datetime import date, timedelta
from typing import Dict, Any


class AnalyticsService:
    """
    Serviço centralizado para cálculos de métricas com comparativos.
    Calcula automaticamente o delta % em relação ao período anterior.
    """

    async def get_overview(self, start_date: date, end_date: date) -> Dict[str, Any]:
        async with AsyncSessionLocal() as db:
            # 1. Dados do Período Atual (Selecionado no Dashboard)
            current_stats = await self._get_period_metrics(db, start_date, end_date)

            # 2. Dados do Período Anterior (Para o Comparativo)
            # Calculamos a duração do período para retroceder a mesma quantidade de dias
            days_diff = (end_date - start_date).days + 1
            prev_start = start_date - timedelta(days=days_diff)
            prev_end = start_date - timedelta(days=1)

            previous_stats = await self._get_period_metrics(db, prev_start, prev_end)

            # 3. Busca os dados diários para o Gráfico (Time-Series)
            stmt_chart = (
                select(
                    CampaignInsight.data,
                    func.sum(CampaignInsight.spend).label("spend"),
                    func.sum(CampaignInsight.revenue).label("revenue"),
                )
                .where(CampaignInsight.data.between(start_date, end_date))
                .group_by(CampaignInsight.data)
                .order_by(CampaignInsight.data)
            )

            res_chart = await db.execute(stmt_chart)
            chart_data = [
                {
                    "date": row.data.strftime("%Y-%m-%d"),
                    "spend": round(float(row.spend or 0), 2),
                    "revenue": round(float(row.revenue or 0), 2),
                }
                for row in res_chart.all()
            ]

            # 4. Função interna para calcular o Crescimento % (Delta)
            def calc_delta(curr: float, prev: float) -> float:
                if not prev or prev == 0:
                    return 0.0
                return round(((curr - prev) / prev) * 100, 2)

            # 5. Montagem do JSON Final com os Deltas
            return {
                "summary": {
                    "revenue": {
                        "value": round(current_stats["revenue"], 2),
                        "delta": calc_delta(
                            current_stats["revenue"], previous_stats["revenue"]
                        ),
                    },
                    "spend": {
                        "value": round(current_stats["spend"], 2),
                        "delta": calc_delta(
                            current_stats["spend"], previous_stats["spend"]
                        ),
                    },
                    "roas": {
                        "value": round(current_stats["roas"], 2),
                        "delta": calc_delta(
                            current_stats["roas"], previous_stats["roas"]
                        ),
                    },
                    "clicks": {
                        "value": current_stats["clicks"],
                        "delta": calc_delta(
                            current_stats["clicks"], previous_stats["clicks"]
                        ),
                    },
                    "ctr": {
                        "value": round(current_stats["ctr"], 4),
                        "delta": calc_delta(
                            current_stats["ctr"], previous_stats["ctr"]
                        ),
                    },
                },
                "chart_data": chart_data,
            }

    async def _get_period_metrics(
        self, db: AsyncSession, start: date, end: date
    ) -> Dict[str, Any]:
        """Auxiliar para buscar somatórios de um período específico."""
        stmt = select(
            func.sum(CampaignInsight.spend).label("spend"),
            func.sum(CampaignInsight.revenue).label("revenue"),
            func.sum(CampaignInsight.clicks).label("clicks"),
            func.sum(CampaignInsight.impressions).label("impressions"),
            func.avg(CampaignInsight.ctr).label("avg_ctr"),
        ).where(CampaignInsight.data.between(start, end))

        res = (await db.execute(stmt)).one()

        spend = float(res.spend or 0)
        revenue = float(res.revenue or 0)

        return {
            "spend": spend,
            "revenue": revenue,
            "clicks": int(res.clicks or 0),
            "impressions": int(res.impressions or 0),
            "roas": (revenue / spend) if spend > 0 else 0.0,
        }


# Instância global para ser importada pelo Router ou pela IA
analytics_service = AnalyticsService()
