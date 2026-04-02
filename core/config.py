import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestão KPIs API"
    
    # URL do banco de dados (ex: postgresql://user:password@localhost/dbname)
    _DATABASE_URL: str = "sqlite:///./test.db"

    @property
    def DATABASE_URL(self) -> str:
        # Se estiver na Vercel (read-only filesystem), usa banco em memória
        if os.environ.get("VERCEL"):
            return "sqlite:///:memory:"
        return self._DATABASE_URL

    class Config:
        env_file = ".env"

settings = Settings()
