import json
from sqlalchemy import Column, String
from sqlalchemy.types import TypeDecorator, String as SQLString
from core.database import Base

class JSONEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = SQLString
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return value
        return value

class Kpi(Base):
    __tablename__ = "kpis"

    id_kpi = Column(String(255), primary_key=True)
    area_negocio = Column(String(255))
    nome_kpi = Column(String(255))
    periodo_referencia = Column(String(255))
    Responsavel = Column(String(255), nullable=True)
    dados_kpi = Column(JSONEncodedDict)  # Salva como String no banco e retorna Dict no Python
