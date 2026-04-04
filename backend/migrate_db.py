import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def migrate():
    print(f"Iniciando migração no banco: {settings.POSTGRES_DB}...")
    
    # Cria o engine assíncrono usando a URL das configurações
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        try:
            # Comando SQL para adicionar a coluna tipo_origem caso ela não exista
            print("Executando: ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS tipo_origem VARCHAR DEFAULT 'PAGO';")
            await conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS tipo_origem VARCHAR DEFAULT 'PAGO';"))
            print("Coluna 'tipo_origem' verificada/adicionada com sucesso.")
        except Exception as e:
            print(f"Erro durante a migração: {e}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
