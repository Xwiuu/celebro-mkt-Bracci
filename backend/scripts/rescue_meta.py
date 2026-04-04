import sys, os, asyncio
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import AsyncSessionLocal
from app.services.meta_service import sync_meta_history

async def run_meta_rescue():
    # 📅 Começando de Abril de 2023 (Dentro dos 37 meses)
    current_start = datetime(2023, 4, 1)
    final_end = datetime.now()
    
    print("🛰️  OPERACAO RESGATE META ADS")
    async with AsyncSessionLocal() as db:
        while current_start < final_end:
            current_end = current_start + timedelta(days=30)
            if current_end > final_end: current_end = final_end
            
            s_str = current_start.strftime("%Y-%m-%d")
            e_str = current_end.strftime("%Y-%m-%d")
            
            try:
                print(f"⏳ Processando Meta: {s_str} ➔ {e_str}")
                await sync_meta_history(db, s_str, e_str)
                await asyncio.sleep(2) # Pausa pro Facebook não te banir
            except Exception as e:
                print(f"❌ Erro no lote {s_str}: {e}")
            
            current_start = current_end + timedelta(days=1)
    print("✅ RESGATE CONCLUÍDO!")

if __name__ == "__main__":
    asyncio.run(run_meta_rescue())