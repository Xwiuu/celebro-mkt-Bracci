import pandas as pd
import io
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.campaign import Campaign
from typing import List, Dict, Any

class ImporterService:
    @staticmethod
    async def process_csv(file_content: bytes, db: AsyncSession) -> Dict[str, Any]:
        # Carrega o CSV usando pandas
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Identifica a plataforma
        columns = [c.lower() for c in df.columns]
        
        if 'campaign name' in columns or 'nome da campanha' in columns:
            return await ImporterService._import_meta(df, db)
        elif 'post' in columns or 'publicação' in columns:
            return await ImporterService._import_mlabs(df, db)
        else:
            raise ValueError("Formato de CSV não reconhecido. Certifique-se de que é um export da Meta Ads ou MLabs.")

    @staticmethod
    async def _import_meta(df: pd.DataFrame, db: AsyncSession) -> Dict[str, Any]:
        # Mapeamento Meta Ads
        # Normaliza nomes de colunas
        df.columns = [c.lower() for c in df.columns]
        
        mapping = {
            'nome': 'campaign name' if 'campaign name' in df.columns else 'nome da campanha',
            'investimento': 'amount spent' if 'amount spent' in df.columns else 'valor gasto',
            'roas': 'roas' if 'roas' in df.columns else 'retorno sobre o investimento em anúncios (roas)',
            'ctr': 'ctr' if 'ctr' in df.columns else 'taxa de cliques (ctr)',
            'cpa': 'cost per result' if 'cost per result' in df.columns else 'custo por resultado'
        }

        count = 0
        for _, row in df.iterrows():
            # Busca se a campanha já existe pelo nome
            stmt = select(Campaign).where(Campaign.nome == row[mapping['nome']])
            result = await db.execute(stmt)
            campaign = result.scalar_one_or_none()

            if not campaign:
                campaign = Campaign(nome=row[mapping['nome']])
                db.add(campaign)

            campaign.plataforma = 'Meta'
            campaign.tipo_origem = 'PAGO'
            campaign.investimento_diario = float(str(row.get(mapping['investimento'], 0)).replace(',', '.'))
            campaign.roas = float(str(row.get(mapping['roas'], 0)).replace(',', '.'))
            campaign.ctr = float(str(row.get(mapping['ctr'], 0)).replace(',', '.'))
            campaign.cpa = float(str(row.get(mapping['cpa'], 0)).replace(',', '.'))
            campaign.status = 'ativa'
            
            count += 1

        await db.commit()
        return {"status": "success", "platform": "Meta Ads", "imported_count": count}

    @staticmethod
    async def _import_mlabs(df: pd.DataFrame, db: AsyncSession) -> Dict[str, Any]:
        # Mapeamento MLabs / Orgânico
        df.columns = [c.lower() for c in df.columns]
        
        mapping = {
            'nome': 'post' if 'post' in df.columns else 'publicação',
            'alcance': 'alcance' if 'alcance' in df.columns else 'reach',
            'engajamento': 'engajamento' if 'engajamento' in df.columns else 'engagement'
        }

        count = 0
        for _, row in df.iterrows():
            stmt = select(Campaign).where(Campaign.nome == row[mapping['nome']])
            result = await db.execute(stmt)
            campaign = result.scalar_one_or_none()

            if not campaign:
                campaign = Campaign(nome=row[mapping['nome']])
                db.add(campaign)

            campaign.plataforma = 'MLabs/Orgânico'
            campaign.tipo_origem = 'ORGANICO'
            campaign.investimento_diario = 0.0  # Orgânico não tem investimento direto
            # No orgânico, podemos mapear engajamento/alcance para métricas aproximadas se necessário
            # mas o model atual é bem focado em Ads. Vamos zerar as métricas de Ads.
            campaign.roas = 0.0
            campaign.ctr = 0.0 
            campaign.cpa = 0.0
            campaign.status = 'orgânica'
            
            count += 1

        await db.commit()
        return {"status": "success", "platform": "MLabs", "imported_count": count}

    @staticmethod
    async def get_campaign_context(db: AsyncSession) -> str:
        """
        Retorna um resumo textual de todas as campanhas para alimentar o contexto da IA.
        """
        stmt = select(Campaign)
        result = await db.execute(stmt)
        campaigns = result.scalars().all()
        
        if not campaigns:
            return "Nenhuma campanha encontrada no banco de dados."
            
        context_lines = []
        for c in campaigns:
            line = f"- Campanha: {c.nome} | Plataforma: {c.plataforma} | Status: {c.status} | ROAS: {c.roas} | CTR: {c.ctr}% | CPA: R${c.cpa} | Investimento: R${c.investimento_diario}"
            context_lines.append(line)
            
        return "\n".join(context_lines)

# Instância única do serviço para exportação
importer_service = ImporterService()
