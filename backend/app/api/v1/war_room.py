import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.groq_service import ai_service
from app.services.obsidian_service import obsidian_service
from app.services.synx_service import synx_service
import traceback

router = APIRouter()

class NegotiateRequest(BaseModel):
    message: str
    history: list = [] # Para manter contexto na negociação

class SanctionRequest(BaseModel):
    final_plan: str
    summary: str

@router.post("/negotiate")
async def negotiate_plan(request: NegotiateRequest):
    """
    Interface de Negociação de Tráfego (William's Second Brain).
    """
    system_prompt = (
        "Você é o Segundo Cérebro do William. Um estrategista de tráfego de alto nível (Neuro-Sócio).\n"
        "William gerencia tanto o Orgânico quanto o Pago. Seu papel é construir o plano ideal iterativamente.\n"
        "DIRETRIZES:\n"
        "1. Orgânico (MLabs): Avalie qualidade de conteúdo e criação de desejo.\n"
        "2. Pago (Meta): Foque em ROAS, CPA e escala matemática.\n"
        "3. CROSS-OVER: Sugira transformar posts orgânicos virais em criativos pagos.\n"
        "Seja direto, frio, matemático e tático."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in request.history:
        messages.append(msg)
    messages.append({"role": "user", "content": request.message})

    try:
        client = await ai_service._get_client()
        chat_completion = await client.chat.completions.create(
            messages=messages,
            model=ai_service.model,
            temperature=0.3,
        )
        return {"response": chat_completion.choices[0].message.content}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro na negociação com a IA.")

@router.post("/sanction")
async def sanction_plan(request: SanctionRequest):
    """
    Sanciona o plano, salva no Obsidian e delega tarefas para o SYNX.
    """
    try:
        # 1. Salvar no Obsidian (Memória de Longo Prazo)
        content = f"""# PLANO DE BATALHA SEMANAL - BRACCI

## RESUMO DA ESTRATÉGIA
{request.summary}

## PLANO FINAL ACORDADO
{request.final_plan}

#plano-semanal #bracci #performance #ia #synx-delegated
"""
        filepath = obsidian_service.save_memory(
            title="PLANO_SEMANAL_SANCIONADO",
            content=content,
            tags=["plano-semanal", "bracci", "sancionado"],
            status="approved"
        )

        # 2. Inteligência de Delegação (Groq como Gerente de Projetos)
        pm_prompt = (
            "Você é um Gerente de Projetos da Bracci. Leia este plano tático de marketing e extraia as tarefas operacionais.\n"
            "REGRAS:\n"
            "1. Retorne ESTRITAMENTE um JSON.\n"
            "2. Estrutura: {'tasks': [{'titulo': str, 'descricao': str, 'departamento': str, 'prioridade': str}]}.\n"
            "3. Departamentos válidos: Design, Copy, Tráfego.\n"
            "4. Prioridades: ALTA, MEDIA, BAIXA."
        )
        
        user_prompt = f"PLANO TÁTICO:\n{request.final_plan}"
        
        client = await ai_service._get_client()
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": pm_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=ai_service.model,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        
        delegation_data = json.loads(chat_completion.choices[0].message.content)
        tasks = delegation_data.get("tasks", [])

        # 3. Disparo de Webhook para o SYNX
        if tasks:
            await synx_service.create_batch_tasks(tasks)

        return {
            "message": "PLANO SANCIONADO. MEMÓRIA NO OBSIDIAN E TAREFAS DELEGADAS AO SYNX.",
            "path": filepath,
            "tasks_count": len(tasks)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro no processamento final: {str(e)}")
