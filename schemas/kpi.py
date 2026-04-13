from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any, Dict, Union
from datetime import date


class KpiBase(BaseModel):
    area_negocio: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Area de negocio responsavel pelo KPI (ex: Geracao, Comercial, Risco).",
        json_schema_extra={"examples": ["Geracao"]},
    )
    nome_kpi: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome do indicador de performance.",
        json_schema_extra={"examples": ["Disponibilidade de Usinas"]},
    )
    periodo_referencia: Union[str, date] = Field(
        ...,
        description="Periodo de referencia do KPI no formato YYYY-MM-DD.",
        json_schema_extra={"examples": ["2026-04-01"]},
    )
    Responsavel: Optional[str] = Field(
        None,
        max_length=255,
        description="Nome do responsavel pelo KPI.",
        json_schema_extra={"examples": ["Joao Silva"]},
    )
    dados_kpi: Dict[str, Any] = Field(
        ...,
        description="Dados do KPI em formato livre (dicionario JSON).",
        json_schema_extra={"examples": [{"valor": 98.5, "meta": 99.0, "unidade": "%"}]},
    )

    @field_validator("periodo_referencia")
    def parse_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v


class KpiCreate(KpiBase):
    id_kpi: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Identificador unico do KPI.",
        json_schema_extra={"examples": ["KPI-GER-001"]},
    )


class KpiUpdate(BaseModel):
    area_negocio: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Area de negocio responsavel pelo KPI.",
        json_schema_extra={"examples": ["Comercial"]},
    )
    nome_kpi: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Nome do indicador de performance.",
        json_schema_extra={"examples": ["Volume Contratado"]},
    )
    periodo_referencia: Optional[Union[str, date]] = Field(
        None,
        description="Periodo de referencia do KPI no formato YYYY-MM-DD.",
        json_schema_extra={"examples": ["2026-04-01"]},
    )
    Responsavel: Optional[str] = Field(
        None,
        max_length=255,
        description="Nome do responsavel pelo KPI.",
        json_schema_extra={"examples": ["Maria Santos"]},
    )
    dados_kpi: Optional[Dict[str, Any]] = Field(
        None,
        description="Dados do KPI em formato livre (dicionario JSON).",
        json_schema_extra={"examples": [{"valor": 120.0, "meta": 100.0, "unidade": "MWh"}]},
    )

    @field_validator("periodo_referencia")
    def parse_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v


class KpiResponse(KpiBase):
    id_kpi: str = Field(..., description="Identificador unico do KPI.")

    class Config:
        from_attributes = True


# --- Schemas de resposta padronizada ---

class ErrorDetail(BaseModel):
    error_code: str = Field(..., description="Codigo do erro.", json_schema_extra={"examples": ["NOT_FOUND"]})
    message: str = Field(..., description="Mensagem descritiva do erro.", json_schema_extra={"examples": ["KPI com id 'XYZ' nao encontrado."]})
    details: Dict[str, Any] = Field(default_factory=dict, description="Detalhes adicionais do erro.")
    timestamp: str = Field(..., description="Timestamp UTC do erro no formato ISO 8601.", json_schema_extra={"examples": ["2026-04-09T14:30:00+00:00"]})
