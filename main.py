import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.config import settings
from core.database import get_bq_client
from core.exceptions import KpiApiError
from controllers import kpi
from utils.security import get_api_key

# ---------------------------------------------------------------------------
# Rate Limiter (por IP)
# ---------------------------------------------------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri="memory://",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validar conexao BigQuery no startup
    try:
        client = get_bq_client()
        dataset_ref = f"{settings.BIGQUERY_PROJECT}.{settings.BIGQUERY_DATASET}"
        client.get_dataset(dataset_ref)
        print(f"[INFO] BigQuery conectado: {dataset_ref}")
    except Exception as e:
        print(f"[WARN] Falha ao validar BigQuery: {e}")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "API para gestao centralizada de KPIs da Matrix - "
        "Comercializadora de Energia Eletrica.\n\n"
        "**Dados:** Consulta a view `vw_kpi_ultimo_valor` no BigQuery "
        f"(projeto: `{settings.BIGQUERY_PROJECT}`, dataset: `{settings.BIGQUERY_DATASET}`).\n\n"
        "**Autenticacao:** Envie o header `X-API-KEY` em todas as requisicoes.\n\n"
        "**Rate Limit:** 60 requisicoes por minuto por IP "
        "(headers `X-RateLimit-Limit` e `X-RateLimit-Remaining` na resposta)."
    ),
    version="2.0.0",
    lifespan=lifespan,
    dependencies=[Depends(get_api_key)],
)

# Registra o rate limiter no app
app.state.limiter = limiter


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Sobrescreve o 422 padrao do FastAPI para usar o nosso formato de erro padrao (400)."""
    return JSONResponse(
        status_code=400,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Erro de validacao nos parametros da requisicao.",
            "details": {"errors": exc.errors()},
        },
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Retorna 429 com mensagem clara quando o rate limit e excedido."""
    return JSONResponse(
        status_code=429,
        content={
            "error_code": "RATE_LIMIT_EXCEEDED",
            "message": f"Limite de requisicoes excedido: {exc.detail}",
            "details": {"limit": str(exc.detail)},
        },
    )


@app.exception_handler(KpiApiError)
async def kpi_api_error_handler(request: Request, exc: KpiApiError):
    """Handler para erros de negocio tipados (NotFound, etc.)."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback para erros inesperados — nunca expoe stack trace ao cliente."""
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "Ocorreu um erro interno no servidor.",
            "details": {"type": type(exc).__name__},
        },
    )


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

app.include_router(kpi.router)


@app.get(
    "/",
    summary="Health Check",
    description="Endpoint raiz para verificar se a API esta no ar.",
    tags=["Health"],
)
def root():
    return {
        "message": "Bem-vindo a API de Gestao de KPIs! Acesse /docs para visualizar os endpoints.",
        "version": "2.0.0",
        "bigquery_project": settings.BIGQUERY_PROJECT,
        "bigquery_dataset": settings.BIGQUERY_DATASET,
    }
