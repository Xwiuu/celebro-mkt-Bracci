import json
from app.services.groq_service import ai_service
from app.services.obsidian_service import obsidian_service
from typing import Dict, Any

class WarRoomService:
    async def generate_weekly_plan(self, global_budget: float, objectives: str) -> Dict[str, Any]:
        """
        Gera um planejamento multicanal (Meta/Google) baseado em orçamento e aprendizados.
        """
        # RAG Simples: Puxa contexto do Obsidian
        past_learnings = obsidian_service.get_recent_memories(limit=3)
        
        system_prompt = (
            "Você é o General de Estratégia da Bracci. Planejador matemático de alto nível.\n"
            "Sua missão é dividir o orçamento entre Meta Ads e Google Ads com foco em ROI.\n"
            "REGRAS:\n"
            "1. Meta Ads: Topo/Meio de Funil (Branding e Desejo).\n"
            "2. Google Ads: Fundo de Funil (Captura de Demanda).\n"
            "3. Retorne ESTRITAMENTE um JSON.\n"
            "4. Chaves: 'meta_plan' (dict), 'google_plan' (dict), 'justificativa_estrategica' (str).\n"
            "5. Cada plano deve ter 'fase_1', 'fase_2' e 'budget_alocado'."
        )
        
        user_prompt = f"""
        ORÇAMENTO GLOBAL: R${global_budget}
        OBJETIVOS: {objectives}
        
        APRENDIZADOS ANTERIORES (CONTEXTO):
        {past_learnings}
        """

        # Usando o Groq para gerar o JSON
        # Nota: GroqService.propose_intervention já tem a estrutura de retry e rotação de chaves.
        # Vou usar uma versão simplificada ou injetar no GroqService se necessário.
        # Por simplicidade, assumindo que GroqService pode lidar com isso.
        
        # Vamos usar o método chat_completion direto do cliente Groq via service se possível,
        # ou apenas reutilizar a lógica de rotação.
        
        client = await ai_service._get_client()
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=ai_service.model,
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        plan = json.loads(chat_completion.choices[0].message.content)
        
        # Salva o plano no Obsidian automaticamente como "Battle Plan"
        obsidian_service.save_memory(
            title=f"Battle Plan - Budget {global_budget}",
            content=json.dumps(plan, indent=4, ensure_ascii=False),
            tags=["battle-plan", "strategy"],
            status="approved_pending"
        )
        
        return plan

war_room_service = WarRoomService()
