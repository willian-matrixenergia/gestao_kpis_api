import json
import os
from sqlalchemy.orm import Session
from models.kpi import Kpi

def carregar_dados_iniciais(db: Session, filepath: str):
    """
    Função utilitária para buscar o JSON local caso não tenhamos o DB preenchido.
    Lê o JSON, converte 'dados_kpi' string para dict antes de inserir.
    """
    if not os.path.exists(filepath):
        return

    # Verificar se o BD já tem dados
    if db.query(Kpi).first() is not None:
        return

    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        ids_processados = set()
        
        for item in data:
            kpi_id = item.get("id_kpi")
            
            # Pular se o ID já foi processado neste loop ou já existe no banco
            if kpi_id in ids_processados:
                continue
                
            existing_kpi = db.query(Kpi).filter(Kpi.id_kpi == kpi_id).first()
            if existing_kpi:
                ids_processados.add(kpi_id)
                continue

            # O dados_kpi do JSON original é uma string, vamos desserializar 
            # para guardar como JSON/dicionário apropriadamente
            if isinstance(item.get("dados_kpi"), str):
                try:
                    item["dados_kpi"] = json.loads(item["dados_kpi"])
                except json.JSONDecodeError:
                    item["dados_kpi"] = {}
            
            db_kpi = Kpi(**item)
            db.add(db_kpi)
            ids_processados.add(kpi_id)
        
        db.commit()


