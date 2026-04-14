from google.cloud import bigquery
from core.config import settings


def _create_bigquery_client() -> bigquery.Client:
    """
    Cria o client do BigQuery de forma lazy.
    Usa GOOGLE_APPLICATION_CREDENTIALS configurado em config.py.
    """
    return bigquery.Client(project=settings.BIGQUERY_PROJECT)


# Client singleton para reutilização
_bq_client: bigquery.Client | None = None


def get_bq_client() -> bigquery.Client:
    """
    Dependência do FastAPI para injetar o client BigQuery.
    Reutiliza o client (thread-safe por design do google-cloud-bigquery).
    """
    global _bq_client
    if _bq_client is None:
        _bq_client = _create_bigquery_client()
    return _bq_client
