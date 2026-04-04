import json
import logging
from groq import AsyncGroq, RateLimitError
from app.core.ai_manager import groq_manager
from app.core.config import settings
from app.services.knowledge_service import knowledge_service
from app.services.web_service import web_service

class GroqService:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    async def _get_client(self) -> AsyncGroq:
        """Obtém o cliente Groq com a chave ativa atual."""
        api_key = await groq_manager.get_active_key()
        return AsyncGroq(api_key=api_key)

    async def propose_intervention(self, campaign_data: dict) -> dict:
        """
        Atua como Neuro-Sócio Bracci para propor intervenções cirúrgicas de performance.
        """
        # Busca contexto estratégico no ChromaDB
        internal_context = await knowledge_service.search_knowledge("estratégia de performance e branding", n_results=2)
        context_str = "\n".join(internal_context) if internal_context else "Sem contexto adicional."

        system_prompt = (
            "Você é o Neuro-Sócio Estrategista da Bracci. Sua visão é baseada em Neuromarketing, "
            "Exclusividade e Alta Performance. Analise os dados e tome uma decisão executiva.\n"
            f"CONTEXTO ESTRATÉGICO INTERNO:\n{context_str}\n\n"
            "REGRAS:\n"
            "1. Retorne ESTRITAMENTE um JSON.\n"
            "2. Chaves: 'tipo_acao' (ESCALAR, PAUSAR, CRIAR_PUBLICO, TROCAR_COPY), "
            "'impacto_estimado' (valor em R$ baseado no ROI atual), "
            "'justificativa_neuro' (foco em gatilhos mentais e psicologia de luxo)."
        )

        user_prompt = f"Dados da Unidade de Performance: {json.dumps(campaign_data)}"

        for _ in range(len(settings.groq_keys_list)):
            client = await self._get_client()
            try:
                chat_completion = await client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    model=self.model,
                    response_format={"type": "json_object"},
                    temperature=0.3, # Consistência com pitada de ousadia
                )
                return json.loads(chat_completion.choices[0].message.content)
            except RateLimitError:
                await groq_manager.rotate_key()
                continue
        raise Exception("Neuro-Sócio offline por Rate Limit.")

    async def generate_ad_copy(self, campaign_name: str, mood: str = "exclusividade") -> dict:
        """
        Gera cópias de anúncios de alta conversão usando Gatilhos Mentais de Luxo.
        """
        system_prompt = (
            "Você é um Senior Copywriter especializado em Mercado de Luxo e Neuromarketing.\n"
            f"Seu tom de voz deve ser: {mood.upper()}.\n"
            "FOCO: Estética, Status, Exclusividade e Qualidade Impecável (Padrão Bracci).\n"
            "REGRAS:\n"
            "1. Retorne ESTRITAMENTE um JSON.\n"
            "2. Chaves: 'headline' (curta e impactante), 'primary_text' (corpo do anúncio com gatilhos), 'description' (chamada para ação).\n"
            "3. Use emojis de forma minimalista e sofisticada (✨, 🏛️, 💎)."
        )

        user_prompt = f"Crie um anúncio de alta performance para o produto/campanha: {campaign_name}"

        for _ in range(len(settings.groq_keys_list)):
            client = await self._get_client()
            try:
                chat_completion = await client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    model=self.model,
                    response_format={"type": "json_object"},
                    temperature=0.7, # Maior criatividade para copy
                )
                return json.loads(chat_completion.choices[0].message.content)
            except RateLimitError:
                await groq_manager.rotate_key()
                continue
        raise Exception("Erro ao gerar copy: Limite de taxa atingido.")

from app.services.knowledge_service import knowledge_service
from app.services.web_service import web_service
from app.services.analytics_service import analytics_service
from app.db.session import AsyncSessionLocal

class GroqService:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    async def _get_client(self) -> AsyncGroq:
        """Obtém o cliente Groq com a chave ativa atual."""
        api_key = await groq_manager.get_active_key()
        return AsyncGroq(api_key=api_key)

    async def terminal_chat(self, user_message: str, context: str) -> str:
        """
        Chat terminal para o Mastermind de Neuromarketing Bracci com RAG, Web Search e Injeção Dinâmica YoY.
        """
        # 1. INJEÇÃO SILENCIOSA DE CONTEXTO ANALÍTICO (YoY + Canais)
        async with AsyncSessionLocal() as db:
            tactical_briefing = await analytics_service.get_full_tactical_context(db)

        # 2. Busca Contexto Interno (RAG do Brand Book / Estratégia)
        internal_knowledge = await knowledge_service.search_knowledge(user_message)
        knowledge_str = "\n".join(internal_knowledge) if internal_knowledge else "Nenhum dado interno encontrado."

        # 3. Busca Web (se necessário)
        web_context = ""
        keywords = ["busque", "pesquise", "internet", "web", "atualidade", "notícias", "mercado hoje"]
        if any(k in user_message.lower() for k in keywords):
            web_context = web_service.search_live_web(user_message)

        system_prompt = (
            "Você é o Celebro, o Mastermind de Neuromarketing da Bracci focado em Alta Performance e Luxo.\n"
            "Sua visão é embasada em neurociência do consumo e análise tática cirúrgica.\n\n"
            "--- DADOS DE PERFORMANCE EM TEMPO REAL (BRACCI ANALYTICS) ---\n"
            f"{tactical_briefing}\n\n"
            "--- CONTEXTO DE MEMÓRIA (BRAND BOOK / RAG) ---\n"
            f"{knowledge_str}\n\n"
            "--- CONTEXTO WEB ATUAL (GOOGLE/DDG) ---\n"
            f"{web_context if web_context else 'Busca web não solicitada.'}\n\n"
            "DIRETRIZES DE OPERAÇÃO:\n"
            "1. Use os dados absolutos de performance (YoY e Share) para embasar qualquer análise solicitada.\n"
            "2. Nunca invente dados. Se o usuário perguntar 'Por que estamos variando?', use o briefing acima.\n"
            "3. Se a performance de um canal estiver caindo (ex: Google -3.8%), sugira uma intervenção neuro-criativa baseada no Brand Book.\n"
            "4. Resposta curta, direta e com autoridade máxima."
        )

        for _ in range(len(settings.groq_keys_list)):
            client = await self._get_client()
            try:
                chat_completion = await client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    model=self.model,
                    temperature=0.2,
                )
                return chat_completion.choices[0].message.content
            except RateLimitError:
                await groq_manager.rotate_key()
                continue
        raise Exception("Estrategista Offline.")

# Instância única do serviço
ai_service = GroqService()
