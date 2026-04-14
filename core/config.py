import os
import tempfile
import json
from pydantic_settings import BaseSettings

# Lógica para carregar credenciais do BigQuery na Vercel a partir de uma variável de ambiente (JSON string)
gcp_creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if gcp_creds_json:
    try:
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

    # BigQuery settings
    BIGQUERY_PROJECT: str = os.getenv("BIGQUERY_PROJECT", "matrix-data-products-prd")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "ds_gestao_kpis")

    # Configuração de Segurança
    API_KEY: str = os.getenv("API_KEY", "matrix_secret_key_2026")
    API_KEY_NAME: str = "X-API-KEY"

    @property
    def BIGQUERY_TABLE_PREFIX(self) -> str:
        """Retorna o prefixo completo para queries BigQuery: `project.dataset`."""
        return f"{self.BIGQUERY_PROJECT}.{self.BIGQUERY_DATASET}"

    @property
    def ENVIRONMENT(self) -> str:
        if os.environ.get("VERCEL"):
            return "production"
        return os.environ.get("ENV", "development")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
