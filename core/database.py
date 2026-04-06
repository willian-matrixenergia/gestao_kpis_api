from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

Base = declarative_base()

def _create_engine():
    """
    Cria a engine de forma lazy para garantir que settings.DATABASE_URL
    seja avaliado após todas as variáveis de ambiente estarem carregadas.
    """
    db_url = settings.DATABASE_URL
    is_sqlite = db_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    return create_engine(db_url, connect_args=connect_args)

engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependência do FastAPI para injetar a sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
