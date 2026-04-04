import asyncio
import logging
from typing import List
from app.core.config import settings

class GroqKeyManager:
    def __init__(self, keys: List[str]):
        if not keys:
            raise ValueError("Nenhuma chave de API do Groq configurada.")
        self._keys = keys
        self._current_index = 0
        self._lock = asyncio.Lock()

    async def get_active_key(self) -> str:
        """Retorna a chave atual de forma thread-safe."""
        async with self._lock:
            return self._keys[self._current_index]

    async def rotate_key(self) -> str:
        """Rotaciona para a próxima chave disponível."""
        async with self._lock:
            self._current_index = (self._current_index + 1) % len(self._keys)
            new_key = self._keys[self._current_index]
            logging.warning(f"Rate limit atingido. Rotacionando para chave no índice {self._current_index}")
            return new_key

# Singleton para uso em toda a aplicação
groq_manager = GroqKeyManager(settings.groq_keys_list)
