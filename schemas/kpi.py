from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class KpiProcessamentoResponse(BaseModel):
    """Schema flat desnormalizado — espelha a view vw_kpi_vs_meta do BigQuery."""

    # Processamento
    id_processamento: str = Field(
        ...,
        description="Identificador unico do processamento.",
        json_schema_extra={"examples": ["PROC-2026-02-C001"]},
    )
    # KPI (dim_kpi)
    id_kpi: str = Field(
        ...,
        description="Identificador unico do KPI.",
        json_schema_extra={"examples": ["receita_trading"]},
    )
    nm_kpi: str = Field(
        ...,
        description="Nome do KPI.",
        json_schema_extra={"examples": ["Receita de Trading Intraday"]},
    )
    nm_bu_kpi: str = Field(
        ...,
        description="Business Unit do KPI.",
        json_schema_extra={"examples": ["BESS"]},
    )
    nm_area_kpi: str = Field(
        ...,
        description="Area do KPI.",
        json_schema_extra={"examples": ["Trading"]},
    )
    nm_responsavel_kpi: str = Field(
        ...,
        description="Email do responsavel pelo KPI.",
        json_schema_extra={"examples": ["lucas.melo@empresa.com"]},
    )
    fl_kpi_ativo: str = Field(
        ...,
        description="Flag indicando se o KPI esta ativo.",
        json_schema_extra={"examples": ["true"]},
    )
    # Regra (dim_regra_kpi)
    id_regra: str = Field(
        ...,
        description="Identificador da regra de calculo.",
        json_schema_extra={"examples": ["regra_004"]},
    )
    ds_regra: str = Field(
        ...,
        description="Descricao da regra de apuracao.",
        json_schema_extra={"examples": ["Soma da receita liquida obtida nas operacoes de compra e venda de energia"]},
    )
    dt_criacao_regra: str = Field(
        ...,
        description="Data de criacao da regra (YYYY-MM-DD).",
        json_schema_extra={"examples": ["2025-02-01"]},
    )
    fl_regra_ativa: str = Field(
        ...,
        description="Flag indicando se a regra esta ativa.",
        json_schema_extra={"examples": ["true"]},
    )
    # Valores realizados (fct_kpi_valor)
    vl_realizado: str = Field(
        ...,
        description="Valor realizado do KPI no periodo.",
        json_schema_extra={"examples": ["135000.0"]},
    )
    dt_referencia: str = Field(
        ...,
        description="Data de referencia do calculo (YYYY-MM-DD).",
        json_schema_extra={"examples": ["2026-02-01"]},
    )
    dt_processamento: str = Field(
        ...,
        description="Data/hora do processamento (ISO 8601).",
        json_schema_extra={"examples": ["2026-03-01T09:00:00"]},
    )
    nm_responsavel_calculo: str = Field(
        ...,
        description="Email do responsavel pelo calculo.",
        json_schema_extra={"examples": ["lucas.melo@empresa.com"]},
    )
    # Meta (dim_meta + fct_meta_valor)
    id_meta: str = Field(
        ...,
        description="Identificador da meta.",
        json_schema_extra={"examples": ["meta_rec_men"]},
    )
    nm_meta: str = Field(
        ...,
        description="Nome da meta.",
        json_schema_extra={"examples": ["Meta Mensal Receita Trading"]},
    )
    nm_bu_meta: str = Field(
        ...,
        description="Business Unit da meta.",
        json_schema_extra={"examples": ["BESS"]},
    )
    nm_area_meta: str = Field(
        ...,
        description="Area da meta.",
        json_schema_extra={"examples": ["Trading"]},
    )
    tp_meta: str = Field(
        ...,
        description="Tipo da meta (Mensal, Semanal, etc).",
        json_schema_extra={"examples": ["Mensal"]},
    )
    vl_meta: str = Field(
        ...,
        description="Valor alvo da meta.",
        json_schema_extra={"examples": ["130000.0"]},
    )
    dt_atualizacao_meta: str = Field(
        ...,
        description="Data/hora da ultima atualizacao da meta (ISO 8601).",
        json_schema_extra={"examples": ["2026-02-01T09:00:00"]},
    )
    # Atingimento (calculado)
    pct_atingimento: str = Field(
        ...,
        description="Percentual de atingimento da meta.",
        json_schema_extra={"examples": ["103.85"]},
    )
    vl_gap_absoluto: str = Field(
        ...,
        description="Diferenca absoluta entre realizado e meta.",
        json_schema_extra={"examples": ["5000.0"]},
    )
    status_atingimento: str = Field(
        ...,
        description="Status do atingimento: atingido, atencao ou critico.",
        json_schema_extra={"examples": ["atingido"]},
    )


class KpiListResponse(BaseModel):
    """Wrapper para lista de KPIs com metadados de paginacao."""
    total: int = Field(..., description="Total de registros encontrados.")
    skip: int = Field(..., description="Registros pulados.")
    limit: int = Field(..., description="Limite da pagina.")
    data: List[KpiProcessamentoResponse] = Field(..., description="Lista de registros.")


# --- Schemas de resposta padronizada ---

class ErrorDetail(BaseModel):
    error_code: str = Field(..., description="Codigo do erro.", json_schema_extra={"examples": ["NOT_FOUND"]})
    message: str = Field(..., description="Mensagem descritiva do erro.", json_schema_extra={"examples": ["Processamento com id 'XYZ' nao encontrado."]})
    details: Dict[str, Any] = Field(default_factory=dict, description="Detalhes adicionais do erro.")
    timestamp: str = Field(..., description="Timestamp UTC do erro no formato ISO 8601.", json_schema_extra={"examples": ["2026-04-09T14:30:00+00:00"]})
