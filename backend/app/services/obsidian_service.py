import os
import yaml
from datetime import datetime
from app.core.config import settings

class ObsidianService:
    def __init__(self):
        self.vault_path = settings.OBSIDIAN_VAULT_PATH
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path, exist_ok=True)

    def save_memory(self, title: str, content: str, tags: list = None, status: str = "draft"):
        """
        Salva uma memória (análise ou plano) no Obsidian Vault.
        """
        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{title.replace(' ', '_')}.md"
        filepath = os.path.join(self.vault_path, filename)
        
        frontmatter = {
            "date": datetime.now().isoformat(),
            "tags": tags or ["ia-learning", "bracci-bunker"],
            "status": status,
            "title": title
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(frontmatter, f, default_flow_style=False)
            f.write("---\n\n")
            f.write(content)
            
        return filepath

    def get_recent_memories(self, limit: int = 5) -> str:
        """
        Lê arquivos recentes para servir de contexto (RAG simplificado).
        """
        if not os.path.exists(self.vault_path):
            return ""
            
        files = sorted(
            [f for f in os.listdir(self.vault_path) if f.endswith(".md")],
            reverse=True
        )[:limit]
        
        context = []
        for file in files:
            with open(os.path.join(self.vault_path, file), "r", encoding="utf-8") as f:
                context.append(f.read())
                
        return "\n\n---\n\n".join(context)

obsidian_service = ObsidianService()
