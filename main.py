import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.database import engine, Base, SessionLocal
from core.config import settings
from core.exceptions import KpiApiError
from controllers import kpi
from utils.helpers import carregar_dados_iniciais
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
    is_bigquery = settings.DATABASE_URL.startswith("bigquery")

    if not is_bigquery:
        try:
            from models.kpi import Kpi
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print(f"[WARN] Falha ao criar tabelas: {e}")

        db = SessionLocal()
        try:
            json_path = os.path.join(os.path.dirname(__file__), "exemplo_extrutura_dados_bd.json")
            carregar_dados_iniciais(db, json_path)
        except Exception as e:
            print(f"[WARN] Falha ao carregar dados iniciais: {e}")
        finally:
            db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "API para gestao centralizada de KPIs da Matrix - "
        "Comercializadora de Energia Eletrica.\n\n"
        "**Autenticacao:** Envie o header `X-API-KEY` em todas as requisicoes.\n\n"
        "**Rate Limit:** 60 requisicoes por minuto por IP "
        "(headers `X-RateLimit-Limit` e `X-RateLimit-Remaining` na resposta)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(get_api_key)],
)

# Registra o rate limiter no app
app.state.limiter = limiter


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

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
    """Handler para erros de negocio tipados (NotFound, Duplicate, etc.)."""
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
        "message": "Bem-vindo a API de Gestao de KPIs! Acesse /docs para visualizar os endpoints."
    }
