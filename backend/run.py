import sys
import asyncio
import uvicorn

# Força o Windows a usar o motor assíncrono que suporta subprocessos (abrir o Chrome)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    # Inicia o servidor com o controle total nas nossas mãos
    # O reload=True permite que o servidor reinicie automaticamente ao detectar mudanças no código
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
