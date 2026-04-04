from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Celebro MKT AI"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    DATABASE_URL: str
    
    GROQ_KEYS: str
    OBSIDIAN_VAULT_PATH: str = "D:/apps/Obsidian/Bracci IA"
    
    SYNX_API_URL: str = "https://api.synx.com/v1"
    SYNX_API_KEY: str = "mock_key"
    
    @property
    def groq_keys_list(self) -> List[str]:
        return [k.strip() for k in self.GROQ_KEYS.split(",") if k.strip()]

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
