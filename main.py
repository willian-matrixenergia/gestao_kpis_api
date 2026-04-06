import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from core.database import engine, Base, SessionLocal
from core.config import settings
from controllers import kpi
from utils.helpers import carregar_dados_iniciais
from utils.security import get_api_key

# Vercel serverless functions podem não executar o lifespan corretamente.
# Garantimos a criação das tabelas na inicialização do módulo.
try:
    from models.kpi import Kpi # Garante que o modelo está registrado
    
    # Criar dataset BigQuery se for o caso
    if settings.DATABASE_URL.startswith("bigquery"):
        from google.cloud import bigquery
        try:
            client = bigquery.Client()
            dataset_id = f"{client.project}.gestao_kpis"
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US" # Ou defina de acordo com sua necessidade
            dataset = client.create_dataset(dataset, timeout=30, exists_ok=True)
            print(f"Dataset {dataset.dataset_id} pronto.")
        except Exception as e:
            print(f"Aviso ao verificar dataset: {e}")

    Base.metadata.create_all(bind=engine)
    
    # Também tenta carregar os dados iniciais aqui caso o lifespan não rode
    db = SessionLocal()
    try:
        json_path = os.path.join(os.path.dirname(__file__), "exemplo_extrutura_dados_bd.json")
        carregar_dados_iniciais(db, json_path)
    finally:
        db.close()
except Exception as e:
    print(f"[WARN] Falha ao criar tabelas no startup global: {e}")

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
