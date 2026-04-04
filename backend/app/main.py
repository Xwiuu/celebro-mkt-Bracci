import sys
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from app.core.config import settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.importer import router as import_router
from app.api.v1.chat import router as chat_router
from app.api.v1.brain import router as brain_router
from app.api.v1.war_room import router as war_room_router
from app.api.v1.radar import router as radar_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.sync import router as sync_router
from app.api.v1 import analytics
from app.api.v1 import dashboard

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuração de CORS para o Frontend Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ... (seus imports iniciais continuam iguais)

# Registro de Rotas - PADRONIZADO
app.include_router(
    campaigns_router, prefix=f"{settings.API_V1_STR}/campaigns", tags=["campaigns"]
)
app.include_router(
    import_router, prefix=f"{settings.API_V1_STR}/import", tags=["import"]
)
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(brain_router, prefix=f"{settings.API_V1_STR}/brain", tags=["brain"])
app.include_router(
    war_room_router, prefix=f"{settings.API_V1_STR}/war-room", tags=["war-room"]
)
app.include_router(radar_router, prefix=f"{settings.API_V1_STR}/radar", tags=["radar"])
app.include_router(sync_router, prefix=f"{settings.API_V1_STR}/sync", tags=["sync"])

# AQUI O AJUSTE:
# Forecast usa seu prefixo próprio
app.include_router(
    forecast_router, prefix=f"{settings.API_V1_STR}/forecast", tags=["forecast"]
)

# Dashboard e Analytics usando o padrão do sistema
app.include_router(
    analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"]
)
app.include_router(
    dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"]
)


@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # Roda a cada 1 hora (3600 segundos)
async def auto_sync_task():
    print("🔄 [AUTO-SYNC] Iniciando atualização programada...")
    from app.db.session import SessionLocal
    from app.services.google_ads_service import sync_google_campaigns
    # from app.services.meta_ads_service import sync_meta_insights  # Ajuste o nome se for diferente
    
    async with SessionLocal() as db:
        try:
            await sync_google_campaigns(db)
            # await sync_meta_insights(db)
            print("✅ [AUTO-SYNC] Dados atualizados com sucesso!")
        except Exception as e:
            print(f"❌ [AUTO-SYNC] Erro: {e}")


@app.get("/")
async def root():
    return {"message": "Celebro MKT API Online", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
