from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.exceptions import NotFoundError, DuplicateError
from schemas.kpi import KpiResponse, KpiCreate, KpiUpdate, ErrorDetail
from services.kpi import kpi_service

router = APIRouter(
    prefix="/kpis",
    tags=["KPIs"],
)

# -- Exemplos reutilizaveis para documentacao de erros --
_responses_not_found = {
    404: {
        "model": ErrorDetail,
        "description": "KPI nao encontrado.",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "NOT_FOUND",
                    "message": "KPI com id 'KPI-XYZ' nao encontrado.",
                    "details": {"resource": "KPI", "id": "KPI-XYZ"},
                    "timestamp": "2026-04-09T14:30:00+00:00",
                }
            }
        },
    }
}

_responses_duplicate = {
    409: {
        "model": ErrorDetail,
        "description": "KPI com este id ja existe.",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "DUPLICATE",
                    "message": "KPI com id 'KPI-GER-001' ja existe.",
                    "details": {"resource": "KPI", "id": "KPI-GER-001"},
                    "timestamp": "2026-04-09T14:30:00+00:00",
                }
            }
        },
    }
}

_responses_validation = {
    422: {
        "description": "Erro de validacao nos dados enviados.",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "area_negocio"],
                            "msg": "Field required",
                            "input": {},
                        }
                    ]
                }
            }
        },
    }
}

_responses_rate_limit = {
    429: {
        "description": "Limite de requisicoes excedido.",
        "content": {
            "application/json": {
                "example": {
                    "error": "Rate limit exceeded: 60 per 1 minute"
                }
            }
        },
    }
}


@router.post(
    "/",
    response_model=KpiResponse,
    status_code=201,
    summary="Criar novo KPI",
    description="Cria um novo KPI no sistema. O campo `id_kpi` deve ser unico.",
    responses={**_responses_duplicate, **_responses_validation, **_responses_rate_limit},
)
def create_kpi(request: Request, kpi: KpiCreate, db: Session = Depends(get_db)):
    db_kpi = kpi_service.get_kpi(db, id_kpi=kpi.id_kpi)
    if db_kpi:
        raise DuplicateError(resource="KPI", resource_id=kpi.id_kpi)
    return kpi_service.create_kpi(db=db, kpi=kpi)


@router.get(
    "/",
    response_model=List[KpiResponse],
    summary="Listar KPIs",
    description=(
        "Retorna a lista de KPIs cadastrados com suporte a paginacao "
        "via `skip` e `limit`."
    ),
    responses={**_responses_rate_limit},
)
def read_kpis(
    request: Request,
    skip: int = Query(0, ge=0, description="Quantidade de registros a pular."),
    limit: int = Query(100, ge=1, le=500, description="Quantidade maxima de registros retornados (max 500)."),
    db: Session = Depends(get_db),
):
    return kpi_service.get_kpis(db, skip=skip, limit=limit)


@router.get(
    "/{id_kpi}",
    response_model=KpiResponse,
    summary="Buscar KPI por ID",
    description="Retorna os dados de um KPI especifico pelo seu identificador unico.",
    responses={**_responses_not_found, **_responses_rate_limit},
)
def read_kpi(request: Request, id_kpi: str, db: Session = Depends(get_db)):
    db_kpi = kpi_service.get_kpi(db, id_kpi=id_kpi)
    if db_kpi is None:
        raise NotFoundError(resource="KPI", resource_id=id_kpi)
    return db_kpi


@router.put(
    "/{id_kpi}",
    response_model=KpiResponse,
    summary="Atualizar KPI",
    description=(
        "Atualiza parcialmente um KPI existente. "
        "Apenas os campos enviados no body serao alterados."
    ),
    responses={**_responses_not_found, **_responses_validation, **_responses_rate_limit},
)
def update_kpi(request: Request, id_kpi: str, kpi: KpiUpdate, db: Session = Depends(get_db)):
    db_kpi = kpi_service.update_kpi(db, id_kpi=id_kpi, kpi=kpi)
    if db_kpi is None:
        raise NotFoundError(resource="KPI", resource_id=id_kpi)
    return db_kpi


@router.delete(
    "/{id_kpi}",
    response_model=KpiResponse,
    summary="Deletar KPI",
    description="Remove permanentemente um KPI do sistema pelo seu identificador.",
    responses={**_responses_not_found, **_responses_rate_limit},
)
def delete_kpi(request: Request, id_kpi: str, db: Session = Depends(get_db)):
    db_kpi = kpi_service.delete_kpi(db, id_kpi=id_kpi)
    if db_kpi is None:
        raise NotFoundError(resource="KPI", resource_id=id_kpi)
    return db_kpi
