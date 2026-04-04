import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Carrega as variáveis do .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def fix_database():
    if not DATABASE_URL:
        print("❌ Erro: DATABASE_URL não encontrada no .env")
        return

    print(f"🔗 Conectando ao banco para manutenção...")
    # Garante o uso do driver asyncpg se não estiver na URL
    engine = create_async_engine(DATABASE_URL)

    try:
        async with engine.begin() as conn:
            print("🛠️  Executando ALTER TABLE...")
            # Adiciona a coluna investimento_total se ela não existir
            await conn.execute(text("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS investimento_total FLOAT DEFAULT 0.0;"))
            print("✅ Coluna 'investimento_total' verificada/adicionada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao atualizar o banco: {str(e)}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_database())
