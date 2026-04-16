from typing import Optional, List

from fastapi import APIRouter, Depends, Request, Query
from google.cloud import bigquery

from core.database import get_bq_client
from core.exceptions import NotFoundError
from schemas.kpi import KpiProcessamentoResponse, KpiListResponse, ErrorDetail
from services.kpi import kpi_service

router = APIRouter(
    prefix="/kpis",
    tags=["KPIs"],
)

# -- Exemplos reutilizaveis para documentacao de erros --
_responses_padrao = {
    400: {
        "model": ErrorDetail,
        "description": "Erro de validacao (ex: parametros invalidos).",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "VALIDATION_ERROR",
                    "message": "Erro de validacao nos parametros da requisicao.",
                    "details": {"errors": []},
                    "timestamp": "2026-04-09T14:30:00+00:00"
                }
            }
        }
    },
    401: {
        "model": ErrorDetail,
        "description": "API Key ausente ou invalida.",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "UNAUTHORIZED",
                    "message": "Acesso negado: API Key invalida.",
                    "details": {},
                    "timestamp": "2026-04-09T14:30:00+00:00"
                }
            }
        }
    },
    429: {
        "description": "Limite de requisicoes excedido.",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Limite de requisicoes excedido: 60 per 1 minute",
                    "details": {"limit": "60/minute"}
                }
            }
        },
    },
    500: {
        "model": ErrorDetail,
        "description": "Erro interno do servidor.",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "INTERNAL_ERROR",
                    "message": "Ocorreu um erro interno no servidor.",
                    "details": {"type": "Exception"},
                    "timestamp": "2026-04-09T14:30:00+00:00"
                }
            }
        }
    }
}

_responses_not_found = {
    404: {
        "model": ErrorDetail,
        "description": "Registro nao encontrado.",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "NOT_FOUND",
                    "message": "Processamento com id 'PROC-XYZ' nao encontrado.",
                    "details": {"resource": "Processamento", "id": "PROC-XYZ"},
                    "timestamp": "2026-04-09T14:30:00+00:00",
                }
            }
        },
    }
}

_all_responses = {**_responses_padrao}
_all_responses_with_not_found = {**_responses_padrao, **_responses_not_found}


@router.get(
    "/",
    response_model=KpiListResponse,
    summary="Listar KPIs processados",
    description=(
        "Retorna a lista de KPIs processados com suporte a filtros "
        "e paginacao via `skip` e `limit`. "
        "Dados originados da view `vw_kpi_ultimo_valor` do BigQuery."
    ),
    responses=_all_responses,
)
def list_kpis(
    request: Request,
    id_kpi: Optional[str] = Query(None, description="Filtrar por identificador do KPI."),
    nm_bu_kpi: Optional[str] = Query(None, description="Filtrar por Business Unit (ex: BESS, GRID)."),
    nm_area_kpi: Optional[str] = Query(None, description="Filtrar por area (ex: Trading, Comercial)."),
    dt_referencia: Optional[str] = Query(None, description="Filtrar por data de referencia (YYYY-MM-DD)."),
    status_atingimento: Optional[str] = Query(None, description="Filtrar por status: atingido, atencao, critico."),
    skip: int = Query(0, ge=0, description="Quantidade de registros a pular."),
    limit: int = Query(100, ge=1, le=500, description="Quantidade maxima de registros retornados (max 500)."),
    client: bigquery.Client = Depends(get_bq_client),
):
    result = kpi_service.get_all(
        client,
        id_kpi=id_kpi,
        nm_bu_kpi=nm_bu_kpi,
        nm_area_kpi=nm_area_kpi,
        dt_referencia=dt_referencia,
        status_atingimento=status_atingimento,
        skip=skip,
        limit=limit,
    )
    return result


@router.get(
    "/processamento/{id_processamento}",
    response_model=KpiProcessamentoResponse,
    summary="Buscar por ID de processamento",
    description="Retorna um registro unico pelo seu identificador de processamento.",
    responses=_all_responses_with_not_found,
)
def get_by_processamento(
    request: Request,
    id_processamento: str,
    client: bigquery.Client = Depends(get_bq_client),
):
    result = kpi_service.get_by_processamento(client, id_processamento)
    if result is None:
        raise NotFoundError(resource="Processamento", resource_id=id_processamento)
    return result


@router.get(
    "/kpi/{id_kpi}",
    response_model=List[KpiProcessamentoResponse],
    summary="Historico de um KPI",
    description=(
        "Retorna todos os registros de processamento de um KPI especifico, "
        "ordenados por data de processamento (mais recente primeiro). "
        "Conforme arquitetura, retorna historico padrao."
    ),
    responses=_all_responses_with_not_found,
)
def get_kpi_history(
    request: Request,
    id_kpi: str,
    client: bigquery.Client = Depends(get_bq_client),
):
    results = kpi_service.get_by_kpi(client, id_kpi)
    if not results:
        raise NotFoundError(resource="KPI", resource_id=id_kpi)
    return results
