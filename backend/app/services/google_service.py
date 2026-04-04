import os
from google.ads.googleads.client import GoogleAdsClient
from app.core.config import settings

class GoogleService:
    def __init__(self):
        # O cliente pode ser carregado de um dicionário (do .env) ou de um arquivo YAML
        self.config = {
            "developer_token": os.getenv("GOOGLE_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True
        }
        self.customer_id = os.getenv("GOOGLE_CUSTOMER_ID")

    def _get_client(self):
        return GoogleAdsClient.load_from_dict(self.config)

    def fetch_campaign_metrics(self):
        """
        Puxa métricas reais das campanhas do Google Ads via GAQL.
        """
        if not self.customer_id:
            return []

        client = self._get_client()
        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                metrics.cost_micros,
                metrics.conversions_value,
                metrics.conversions
            FROM campaign
            WHERE segments.date DURING LAST_30_DAYS
        """

        results = []
        try:
            stream = ga_service.search_stream(customer_id=self.customer_id, query=query)
            for batch in stream:
                for row in batch.results:
                    # Google Ads usa 'micros' (1,000,000 = 1 unidade monetária)
                    spend = row.metrics.cost_micros / 1_000_000
                    revenue = row.metrics.conversions_value
                    roas = revenue / spend if spend > 0 else 0.0
                    cpa = spend / row.metrics.conversions if row.metrics.conversions > 0 else 0.0

                    results.append({
                        "external_id": str(row.campaign.id),
                        "nome": row.campaign.name,
                        "plataforma": "Google",
                        "investimento": spend,
                        "receita": revenue,
                        "roas": roas,
                        "cpa": cpa
                    })
        except Exception as e:
            print(f"Erro ao buscar Google Ads: {str(e)}")
            return []
            
        return results

google_service = GoogleService()
