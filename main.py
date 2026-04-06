import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from core.database import engine, Base, SessionLocal
from core.config import settings
from controllers import kpi
from utils.helpers import carregar_dados_iniciais
from utils.security import get_api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas associadas aos modelos se ainda não existirem
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[WARN] Falha ao criar tabelas: {e}")

    # Popula o BD mock localmente se existir o json no repositório 
    # e a tabela estiver vazia. Na Vercel (banco em memória), o JSON
    # não existe no filesystem, então o carregamento é ignorado silenciosamente.
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
    description="API para testes de gestão de KPIs com CRUD completo.",
    lifespan=lifespan,
    dependencies=[Depends(get_api_key)]
)

app.include_router(kpi.router)

@app.get("/")
def root():
    return {"message": "Bem-vindo à API de Gestão de KPIs! Acesse /docs para visualizar os endpoints."}
