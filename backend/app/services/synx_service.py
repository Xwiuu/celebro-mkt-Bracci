import httpx
import logging
from app.core.config import settings
from typing import List, Dict, Any

class SynxService:
    def __init__(self):
        self.api_url = settings.SYNX_API_URL
        self.api_key = settings.SYNX_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Envia uma tarefa extraída pela IA para o sistema SYNX.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/tasks",
                    json=task_data,
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code in [200, 201]:
                    logging.info(f"Tarefa SYNX criada: {task_data.get('titulo')}")
                    return True
                else:
                    logging.error(f"Erro ao criar tarefa SYNX: {response.text}")
                    return False
            except Exception as e:
                logging.error(f"Falha de conexão com SYNX: {str(e)}")
                return False

    async def create_batch_tasks(self, tasks: List[Dict[str, Any]]):
        """
        Cria múltiplas tarefas no SYNX.
        """
        results = []
        for task in tasks:
            success = await self.create_task(task)
            results.append(success)
        return results

synx_service = SynxService()
