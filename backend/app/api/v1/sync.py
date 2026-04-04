from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.redis import cache_service

# Importamos os dois serviços (Meta e Google)
from app.services.meta_service import sync_meta_campaigns
from app.services.google_ads_service import sync_google_campaigns  # <-- O novo reforço!

router = APIRouter()


@router.post("/platforms")
async def sync_platforms(db: AsyncSession = Depends(get_db)):
    """
    Sincronização OMNICHANNEL:
    Puxa dados da Meta e do Google Ads simultaneamente para o PostgreSQL.
    """
    try:
        print("🚀 [SYNC] Iniciando Protocolo Omnichannel Bracci...")

        # 1. Sincroniza Meta Ads (Time-Series)
        print("🔹 [META] Sincronizando dados do Facebook/Instagram...")
        await sync_meta_campaigns(db)

        # 2. Sincroniza Google Ads (Time-Series)
        print("🔸 [GOOGLE] Sincronizando dados de Pesquisa/Youtube/Display...")
        await sync_google_campaigns(db)

        # 🔥 LIMPA O CACHE DO REDIS
        cache_service.client.flushdb()  # Limpa TUDO no Redis pra garantir que os dados antigos sumiram
        print("🗑️ Redis completamente limpo!")

        return {
            "status": "success",
            "message": "Sincronização OMNICHANNEL concluída! Meta + Google integrados no banco.",
            "protocol": "Delta-Alpha-2026",
        }

    except Exception as e:
        print(f"❌ [CRITICAL ERROR] Falha no Sync: {str(e)}")
        # Se um falhar, a gente avisa onde foi o B.O.
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")
