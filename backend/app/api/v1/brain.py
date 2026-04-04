import json
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from app.services.groq_service import ai_service
from app.services.obsidian_service import obsidian_service
from app.services.war_room_service import war_room_service
from app.services.knowledge_service import knowledge_service

router = APIRouter()

class BattlePlanRequest(BaseModel):
    global_budget: float
    objectives: str

class SaveMemoryRequest(BaseModel):
    title: str
    content: str
    tags: list = []

@router.post("/upload")
async def upload_to_brain(
    file: UploadFile = File(...),
    category: str = Form("BRANDING")
):
    """
    Endpoint para 'Upload de Consciência'. Salva documentos (PDF/TXT) no ChromaDB.
    """
    try:
        content = await file.read()
        result = await knowledge_service.upload_document(
            file_content=content,
            filename=file.filename,
            category=category
        )
        
        if result.get("status") == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@router.post("/analyze-creative")
async def analyze_creative(
    file: UploadFile = File(...),
    campaign_context: str = Form("performance")
):
    """
    Analisa um criativo (simulação de visão) e gera insights de gatilhos mentais.
    """
    # Em uma implementação real, usaríamos Llama-3-Vision ou similar.
    # Aqui simulamos a análise tática focada em Bracci.
    
    system_prompt = (
        "Você é um Analista de Criativos da Bracci. Especialista em Neuromarketing e Estética de Luxo.\n"
        "REGRAS:\n"
        "1. Analise o criativo recebido (simulado).\n"
        "2. Identifique: Gatilhos Mentais, Composição Visual, e Sugestão de Melhoria.\n"
        "3. Retorne um JSON tático."
    )
    
    user_prompt = f"Analise o criativo '{file.filename}' no contexto de {campaign_context}."

    client = await ai_service._get_client()
    chat_completion = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=ai_service.model,
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    
    analysis = json.loads(chat_completion.choices[0].message.content)
    
    return {
        "analysis": analysis,
        "filename": file.filename,
        "message": "Análise de criativo concluída com sucesso."
    }

@router.post("/generate-battle-plan")
async def generate_battle_plan(request: BattlePlanRequest):
    """
    Gera o planejamento semanal multicanal.
    """
    try:
        plan = await war_room_service.generate_weekly_plan(
            request.global_budget, 
            request.objectives
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no War Room: {str(e)}")

@router.post("/save-to-obsidian")
async def save_to_obsidian(request: SaveMemoryRequest):
    """
    Salva manualmente uma mensagem ou análise no Obsidian.
    """
    try:
        filepath = obsidian_service.save_memory(
            title=request.title,
            content=request.content,
            tags=request.tags + ["manual-save"],
            status="archived"
        )
        return {"message": "Memória persistida no Obsidian.", "path": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
