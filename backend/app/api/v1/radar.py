from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.services.radar_service import radar_service
from pydantic import BaseModel

router = APIRouter()

class ScanRequest(BaseModel):
    page_id: str = "418295661555191"

@router.post("/scan")
async def radar_scan(request: ScanRequest):
    """
    Inicia uma varredura de radar.
    Usamos run_in_threadpool para executar o scraping síncrono sem bloquear o event loop.
    """
    try:
        # 1. Extração Síncrona via Threadpool
        # Isso evita conflitos entre o asyncio do FastAPI e o Playwright Sync no Windows.
        ads = await run_in_threadpool(radar_service.scrape_meta_ads, request.page_id)
        
        # 2. Análise Assíncrona via Groq
        analysis = await radar_service.analyze_competitor(ads)
        
        return {
            "status": "success",
            "page_id": request.page_id,
            "ads_count": len(ads),
            "tactical_alert": analysis
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"FALHA NO RADAR: {str(e)}")
