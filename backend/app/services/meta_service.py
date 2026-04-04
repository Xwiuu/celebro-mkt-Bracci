import os
import httpx
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import cast, String
from app.models.campaign import Campaign, CampaignInsight
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

# Força carregar o .env
load_dotenv()

# Configurações de Acesso
_ID_BRUTO = os.getenv("META_AD_ACCOUNT_ID")
META_AD_ACCOUNT_ID = f"act_{_ID_BRUTO}" if _ID_BRUTO and not str(_ID_BRUTO).startswith("act_") else _ID_BRUTO
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
API_VERSION = "v19.0"
BASE_URL = "https://graph.facebook.com"

async def sync_meta_campaigns(db: AsyncSession):
    """
    Sincronização Master: Busca Campanhas e Insights Diários (Time-Series)
    incluindo Spend, Clicks, Impressions e Revenue (Faturamento).
    """
    print(f"🚀 Iniciando extração FULL TIME-SERIES da conta: {META_AD_ACCOUNT_ID}")
    
    if not META_ACCESS_TOKEN or not META_AD_ACCOUNT_ID:
        raise ValueError("❌ Erro: Credenciais da Meta não encontradas no .env")

    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        # --- PASSO 1: Sincronizar Estrutura de Campanhas ---
        campaigns_url = f"{BASE_URL}/{API_VERSION}/{META_AD_ACCOUNT_ID}/campaigns"
        campaigns_params = {"fields": "id,name,status", "limit": "500"}
        
        print("📡 Coletando lista de campanhas...")
        while campaigns_url:
            camp_res = await client.get(campaigns_url, params=campaigns_params, headers=headers)
            camp_res.raise_for_status()
            camp_json = camp_res.json()
            
            for c_data in camp_json.get("data", []):
                stmt = select(Campaign).where(cast(Campaign.id, String) == str(c_data["id"]))
                res = await db.execute(stmt)
                db_camp = res.scalar_one_or_none()
                
                if not db_camp:
                    db.add(Campaign(id=str(c_data["id"]), nome=c_data["name"], status=c_data["status"]))
                else:
                    db_camp.nome = c_data["name"]
                    db_camp.status = c_data["status"]
            
            await db.commit()
            campaigns_url = camp_json.get("paging", {}).get("next")
            campaigns_params = None

        # --- PASSO 2: Sincronizar Insights Diários (Métricas Financeiras) ---
        # Buscamos os últimos 31 dias para cobrir o mês de Março completo
        since_date = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')
        until_date = datetime.now().strftime('%Y-%m-%d')
        
        insights_url = f"{BASE_URL}/{API_VERSION}/{META_AD_ACCOUNT_ID}/insights"
        insights_params = {
            "level": "campaign",
            "time_increment": "1",
            "time_range": f"{{\"since\":\"{since_date}\",\"until\":\"{until_date}\"}}",
            "fields": "campaign_id,spend,clicks,impressions,ctr,action_values", # Adicionado action_values
            "filtering": "[{'field':'impressions','operator':'GREATER_THAN','value':0}]",
            "limit": "150" # Limite seguro para processar conversões sem dar 500
        }
        
        print(f"📅 Buscando extrato diário de {since_date} até {until_date}...")
        
        total_processado = 0
        while insights_url:
            ins_res = await client.get(insights_url, params=insights_params, headers=headers)
            ins_res.raise_for_status()
            ins_json = ins_res.json()
            
            rows = ins_json.get("data", [])
            for row in rows:
                c_id = str(row.get("campaign_id"))
                data_dia = datetime.strptime(row.get("date_start"), "%Y-%m-%d").date()
                
                # Extração de Métricas
                spend = float(row.get("spend", 0))
                
                # Captura o Revenue (Faturamento) procurando o campo 'purchase' ou 'offsite_conversion.fb_pixel_purchase'
                revenue = 0.0
                action_values = row.get("action_values", [])
                for val in action_values:
                    if val.get("action_type") in ["purchase", "offsite_conversion.fb_pixel_purchase", "onsite_conversion.purchase"]:
                        revenue += float(val.get("value", 0))

                # Cálculo do ROAS
                roas = (revenue / spend) if spend > 0 else 0.0

                query_ins = select(CampaignInsight).where(
                    cast(CampaignInsight.campaign_id, String) == c_id,
                    CampaignInsight.data == data_dia
                )
                res_ins = await db.execute(query_ins)
                db_insight = res_ins.scalar_one_or_none()
                
                metrics = {
                    "spend": spend,
                    "revenue": revenue,
                    "roas": roas,
                    "clicks": int(row.get("clicks", 0)),
                    "impressions": int(row.get("impressions", 0)),
                    "ctr": float(row.get("ctr", 0))
                }
                
                if not db_insight:
                    db.add(CampaignInsight(campaign_id=c_id, data=data_dia, **metrics))
                else:
                    for key, value in metrics.items():
                        setattr(db_insight, key, value)
            
            await db.commit()
            total_processado += len(rows)
            print(f"📊 Processados {total_processado} registros diários...")
            
            # 🔄 Próxima página (Se houver)
            insights_url = ins_json.get("paging", {}).get("next")
            insights_params = None

        print(f"🏁 Sincronização FINALIZADA! Total de registros: {total_processado}")


async def sync_meta_history(db: AsyncSession, start_date: str, end_date: str):
    """Sincroniza histórico do Meta Ads com datas dinâmicas (espelho do Google)."""
    access_token = os.getenv("META_ACCESS_TOKEN")
    ad_account_id = os.getenv("META_AD_ACCOUNT_ID")
    
    if not access_token or not ad_account_id:
        print("❌ Meta Ads: Token ou ID da conta não configurados.")
        return

    # Garante formato correto do account ID
    if ad_account_id and not str(ad_account_id).startswith("act_"):
        ad_account_id = f"act_{ad_account_id}"

    FacebookAdsApi.init(access_token=access_token)
    account = AdAccount(ad_account_id)

    fields = [
        'campaign_id', 'campaign_name', 'spend', 
        'actions', 'clicks', 'impressions', 'action_values'
    ]
    
    # Parâmetros de data para o lote
    params = {
        'level': 'campaign',
        'time_range': {'since': start_date, 'until': end_date},
        'time_increment': 1,  # Traz dia por dia
    }

    print(f"⏳ [HISTÓRICO META] Extraindo de {start_date} até {end_date}...")
    insights = account.get_insights(fields=fields, params=params)

    count = 0
    for entry in insights:
        camp_id = entry.get('campaign_id')
        data_dia = datetime.strptime(entry.get('date_start'), "%Y-%m-%d").date()
        
        spend = float(entry.get('spend', 0))
        
        # No Facebook, revenue costuma vir como 'purchase' nas actions
        revenue = 0.0
        actions = entry.get('actions', [])
        for action in actions:
            if action.get('action_type') in ['offsite_conversion.fb_pixel_purchase', 'purchase', 'onsite_conversion.purchase']:
                revenue += float(action.get('value', 0))

        # 1. Garante que a Campanha existe
        res_camp = await db.execute(
            select(Campaign).where(cast(Campaign.id, String) == camp_id)
        )
        db_camp = res_camp.scalar_one_or_none()
        
        if not db_camp:
            db.add(
                Campaign(
                    id=camp_id, 
                    nome=entry.get('campaign_name', 'Unknown'), 
                    plataforma="Meta", 
                    status="ACTIVE"
                )
            )
            await db.flush()

        # 2. Upsert do Insight
        res_ins = await db.execute(
            select(CampaignInsight).where(
                cast(CampaignInsight.campaign_id, String) == camp_id, 
                CampaignInsight.data == data_dia
            )
        )
        db_ins = res_ins.scalar_one_or_none()
        
        payload = {
            "spend": spend,
            "revenue": revenue,
            "clicks": int(entry.get('clicks', 0)),
            "impressions": int(entry.get('impressions', 0)),
            "platform": "meta",
            "roas": (revenue/spend) if spend > 0 else 0
        }

        if not db_ins:
            db.add(CampaignInsight(campaign_id=camp_id, data=data_dia, **payload))
        else:
            for k, v in payload.items():
                setattr(db_ins, k, v)
        
        count += 1

    await db.commit()
    print(f"✅ Meta: {count} registros salvos no lote {start_date} até {end_date}.")