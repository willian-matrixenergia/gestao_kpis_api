import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from core.database import engine, Base, SessionLocal
from core.config import settings
from controllers import kpi
from utils.helpers import carregar_dados_iniciais
from utils.security import get_api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    # No BigQuery, a criação de tabelas via SQLAlchemy (create_all) é pesada e causa 
    # timeout na inicialização das serverless functions da Vercel. Assumimos que
    # no BigQuery a tabela já foi criada via console ou dbt.
    is_bigquery = settings.DATABASE_URL.startswith("bigquery")
    
    if not is_bigquery:
        # Cria as tabelas associadas aos modelos se ainda não existirem (SQLite local)
        try:
            from models.kpi import Kpi
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print(f"[WARN] Falha ao criar tabelas: {e}")

        # Popula o BD mock localmente se existir o json no repositório 
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
    description="API para gestão de KPIs integrada ao BigQuery.",
    lifespan=lifespan,
    dependencies=[Depends(get_api_key)]
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Ocorreu um erro interno no servidor.", "details": str(exc)},
    )

app.include_router(kpi.router)

@app.get("/")
def root():
    return {"message": "Bem-vindo à API de Gestão de KPIs! Acesse /docs para visualizar os endpoints."}
