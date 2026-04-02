from pydantic import BaseModel
from typing import Optional, Any, Dict

class KpiBase(BaseModel):
    area_negocio: str
    nome_kpi: str
    periodo_referencia: str
    Responsavel: Optional[str] = None
    dados_kpi: Dict[str, Any]  # O FastAPI fará a conversão automática de e para dicionário

class KpiCreate(KpiBase):
    id_kpi: str

class KpiUpdate(BaseModel):
    area_negocio: Optional[str] = None
    nome_kpi: Optional[str] = None
    periodo_referencia: Optional[str] = None
    Responsavel: Optional[str] = None
    dados_kpi: Optional[Dict[str, Any]] = None

class KpiResponse(KpiBase):
    id_kpi: str

    class Config:
        from_attributes = True
