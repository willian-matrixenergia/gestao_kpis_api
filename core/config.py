import os
import tempfile
import json
from pydantic_settings import BaseSettings

# Lógica para carregar credenciais do BigQuery na Vercel a partir de uma variável de ambiente (JSON string)
gcp_creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if gcp_creds_json:
    try:
        # Apenas tenta validar se é um json e se a Vercel não jogou aspas duplas escapadas por acidente
        parsed = json.loads(gcp_creds_json)
        
        creds_path = os.path.join(tempfile.gettempdir(), "bigquery_credentials.json")
        with open(creds_path, "w") as f:
            json.dump(parsed, f)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    except Exception as e:
        print(f"[WARN] Error loading GOOGLE_CREDENTIALS_JSON: {e}")
else:
    # Fallback para ambiente local, se existir o arquivo na raiz
    local_creds = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bigquery_credentials.json")
    if os.path.exists(local_creds):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestão KPIs API"
    
    # URL do banco de dados para BigQuery
    # bigquery://project_id/dataset_id
    _DATABASE_URL: str = "bigquery://matrix-plataforma-dados-dev/ds_refined_gestao_kpis"

    # Configuração de Segurança
    API_KEY: str = os.getenv("API_KEY", "matrix_secret_key_2026")
    API_KEY_NAME: str = "X-API-KEY"

    @property
    def ENVIRONMENT(self) -> str:
        if os.environ.get("VERCEL"):
            return "production"
        return os.environ.get("ENV", "development")

    @property
    def DATABASE_URL(self) -> str:
        return self._DATABASE_URL

    class Config:
        env_file = ".env"

settings = Settings()
