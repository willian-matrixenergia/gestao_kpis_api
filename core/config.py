from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestão KPIs API"
    
    # URL do banco de dados (ex: postgresql://user:password@localhost/dbname)
    # Valor padrão aponta para um SQLite local para facilitar testes rápidos (dados mockados)
    DATABASE_URL: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"

settings = Settings()
