from sqlalchemy import Column, String, JSON
from core.database import Base

class Kpi(Base):
    __tablename__ = "kpis"

    id_kpi = Column(String, primary_key=True, index=True)
    area_negocio = Column(String, index=True)
    nome_kpi = Column(String)
    periodo_referencia = Column(String)
    Responsavel = Column(String, nullable=True)
    dados_kpi = Column(JSON)  # Utilizando JSON agnóstico que atende SQLite e Postgres
