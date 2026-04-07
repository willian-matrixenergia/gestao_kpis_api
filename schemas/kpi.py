from pydantic import BaseModel, field_validator
from typing import Optional, Any, Dict, Union
from datetime import date

class KpiBase(BaseModel):
    area_negocio: str
    nome_kpi: str
    periodo_referencia: Union[str, date]
    Responsavel: Optional[str] = None
    dados_kpi: Dict[str, Any]  # O FastAPI fará a conversão automática de e para dicionário

    @field_validator('periodo_referencia')
    def parse_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v

class KpiCreate(KpiBase):
    id_kpi: str

class KpiUpdate(BaseModel):
    area_negocio: Optional[str] = None
    nome_kpi: Optional[str] = None
    periodo_referencia: Optional[Union[str, date]] = None
    Responsavel: Optional[str] = None
    dados_kpi: Optional[Dict[str, Any]] = None

    @field_validator('periodo_referencia')
    def parse_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v

class KpiResponse(KpiBase):
    id_kpi: str

    class Config:
        from_attributes = True
