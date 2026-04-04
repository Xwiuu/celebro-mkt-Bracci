import sys
import os
import asyncio
from datetime import datetime, timedelta

# Resolve o caminho para encontrar a pasta 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import AsyncSessionLocal
from app.services.google_ads_service import sync_google_history
from app.services.meta_service import sync_meta_history

async def run_full_migration():
    # 📅 INÍCIO: Março de 2023
    current_start = datetime(2023, 3, 1)
    # 🏁 FIM: Hoje
    final_end = datetime.now()
    
    print("🛰️  SISTEMA DE SINCRONIZAÇÃO OMNICHANNEL 2023-2026")
    print("===============================================")

    async with AsyncSessionLocal() as db:
        while current_start < final_end:
            # Lotes de 30 dias para não estourar a API
            current_end = current_start + timedelta(days=30)
            if current_end > final_end:
                current_end = final_end
            
            s_str = current_start.strftime("%Y-%m-%d")
            e_str = current_end.strftime("%Y-%m-%d")
            
            print(f"\n🚀 [LOTE] {s_str} ➔ {e_str}")
            
            # --- GOOGLE ADS ---
            try:
                await sync_google_history(db, s_str, e_str)
            except Exception as e:
                print(f"❌ Erro Google no lote {s_str}: {e}")

            # --- META ADS ---
            try:
                await sync_meta_history(db, s_str, e_str)
            except Exception as e:
                print(f"❌ Erro Meta no lote {s_str}: {e}")
            
            # Pausa técnica para as APIs não bloquearem o IP
            await asyncio.sleep(2)
            
            # Pula para o próximo mês
            current_start = current_end + timedelta(days=1)

    print("\n✅ OPERAÇÃO FINALIZADA COM SUCESSO!")

if __name__ == "__main__":
    asyncio.run(run_full_migration())