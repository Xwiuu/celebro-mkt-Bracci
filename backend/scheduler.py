import asyncio
import schedule
import time
from datetime import datetime
from app.services.meta_service import sync_meta_campaigns
from app.db.session import AsyncSessionLocal

async def run_sync():
    print(f"🕒 [{datetime.now()}] Iniciando Sincronização Automática...")
    async with AsyncSessionLocal() as db:
        try:
            await sync_meta_campaigns(db)
            print(f"✅ [{datetime.now()}] Sincronização concluída com sucesso!")
        except Exception as e:
            print(f"❌ [{datetime.now()}] Erro na sincronização: {e}")

def job():
    # Como o schedule é síncrono e nosso sync é assíncrono, usamos o loop
    asyncio.run(run_sync())

# Agendamento
# 1. Roda todo dia às 05:00 da manhã
schedule.every().day.at("05:00").do(job)

# 2. (Opcional) Roda uma vez a cada 6 horas para manter o Spend atualizado
schedule.every(6).hours.do(job)

if __name__ == "__main__":
    print("🤖 Agendador do Celebro MKT iniciado!")
    print("📅 Próximas sincronizações agendadas para 05:00 AM e a cada 6h.")
    
    # Roda uma vez logo que liga para garantir que o banco tá fresco
    job()
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Verifica a cada minuto