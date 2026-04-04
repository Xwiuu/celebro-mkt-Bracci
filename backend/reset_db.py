import asyncio
from sqlalchemy.ext.asyncio import AsyncConnection
from app.db.session import engine
from app.models.campaign import Base    

async def reset_database():
    print("\n" + "="*50)
    print("🧠 CELEBRO MKT - RECONSTRUÇÃO DO CÉREBRO DIGITAL")
    print("="*50)
    
    async with engine.begin() as conn:
        print("\n🔥 Implodindo tabelas antigas...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Implosão concluída com sucesso!")
        
        print("\n🏗️ Construindo novo schema PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Novo schema criado exatamente como nos modelos SQLAlchemy!")

    print("\n" + "="*50)
    print("🚀 BANCO DE DADOS RESETADO E PRONTO PARA O COMBATE!")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(reset_database())
