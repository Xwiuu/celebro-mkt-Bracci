from duckduckgo_search import DDGS
from typing import List

class WebService:
    def search_live_web(self, query: str, max_results: int = 3) -> str:
        """
        Busca os resultados mais relevantes da internet atual e retorna formatado.
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                if not results:
                    return "A busca na web não retornou resultados relevantes."
                
                formatted_results = []
                for idx, r in enumerate(results, 1):
                    formatted_results.append(
                        f"Resultado {idx}:\nTítulo: {r.get('title')}\n"
                        f"Snippet: {r.get('body')}\n"
                        f"URL: {r.get('href')}"
                    )
                
                return "\n\n---\n\n".join(formatted_results)
        except Exception as e:
            return f"Erro ao realizar busca na web: {str(e)}"

web_service = WebService()
