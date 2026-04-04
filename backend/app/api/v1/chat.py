from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.groq_service import ai_service
from app.services.importer_service import ImporterService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/message")
async def chat_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Terminal Conversacional de Inteligência Fria.
    """
    try:
        # Busca o contexto atual das campanhas
        context = await ImporterService.get_campaign_context(db)
        
        # Envia para o Groq
        response = await ai_service.terminal_chat(request.message, context)
        
        return {"response": response}
    except Exception as e:
        print(f"Erro no Chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Estrategista Offline ou falha no processamento.")
