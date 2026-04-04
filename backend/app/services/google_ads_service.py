import os
from dotenv import load_dotenv

# 🔥 Força o carregamento do .env da raiz do projeto
# O caminho '../../.env' sobe duas pastas a partir de app/services
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import cast, String
from app.models.campaign import Campaign, CampaignInsight
from app.core.normalizer import DataNormalizer


def get_google_ads_client():
    google_ads_config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip(),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "").strip(),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID", "").strip(),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET", "").strip(),
        "use_proto_plus": True,
    }
    login_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").replace("-", "").strip()
    if login_id:
        google_ads_config["login_customer_id"] = login_id
    return GoogleAdsClient.load_from_dict(google_ads_config)


async def sync_google_history(db: AsyncSession, start_date: str, end_date: str):
    """Sincroniza histórico do Google Ads com datas dinâmicas."""
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "").strip()
    client = get_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT 
            campaign.id, campaign.name, segments.date, 
            metrics.cost_micros, metrics.conversions_value,
            metrics.clicks, metrics.impressions
        FROM campaign 
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND metrics.cost_micros > 0
    """

    print(f"⏳ [HISTÓRICO GOOGLE] Extraindo de {start_date} até {end_date}...")
    response = ga_service.search(customer_id=customer_id, query=query)

    count = 0
    for row in response:
        camp_id = str(row.campaign.id)
        data_dia = datetime.strptime(row.segments.date, "%Y-%m-%d").date()
        
        # USA O NORMALIZER PARA GARANTIR BRL
        spend = DataNormalizer.to_brl(row.metrics.cost_micros, "google")
        revenue = DataNormalizer.to_brl(row.metrics.conversions_value, "google")

        print(f"📊 Processando: {row.campaign.name} | Data: {data_dia} | Gasto: R$ {spend}")

        # 1. Garante que a Campanha existe
        res_camp = await db.execute(
            select(Campaign).where(cast(Campaign.id, String) == camp_id)
        )
        db_camp = res_camp.scalar_one_or_none()

        if not db_camp:
            db.add(
                Campaign(
                    id=camp_id,
                    nome=row.campaign.name,
                    plataforma="Google",
                    status=str(row.campaign.status),
                )
            )
            await db.flush()

        # 2. Upsert do Insight (Garante que não duplica e que salva o valor novo)
        res_ins = await db.execute(
            select(CampaignInsight).where(
                cast(CampaignInsight.campaign_id, String) == camp_id,
                CampaignInsight.data == data_dia,
            )
        )
        db_ins = res_ins.scalar_one_or_none()

        payload = {
            "spend": spend,
            "revenue": revenue,
            "clicks": int(row.metrics.clicks) if row.metrics.clicks else 0,
            "impressions": int(row.metrics.impressions) if row.metrics.impressions else 0,
            "platform": "google",
            "roas": (revenue / spend) if spend > 0 else 0,
        }

        if not db_ins:
            db.add(CampaignInsight(campaign_id=camp_id, data=data_dia, **payload))
        else:
            for k, v in payload.items():
                setattr(db_ins, k, v)

        count += 1

    await db.commit()
    print(f"✅ Lote {start_date} até {end_date} finalizado! {count} registros salvos.")


async def sync_google_campaigns(db: AsyncSession):
    """Wrapper que chama sync_google_history com os últimos 30 dias."""
    start_date = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    await sync_google_history(db, start_date, end_date)
