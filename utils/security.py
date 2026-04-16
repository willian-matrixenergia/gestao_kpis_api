import secrets
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
from core.config import settings
from core.exceptions import UnauthorizedError

# Define o componente que lerá a chave do cabeçalho X-API-KEY
api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header_value: str = Security(api_key_header)):
    """
    Dependência que valida se a API Key fornecida no header coincide com a configurada.
    """
    # Verifica se a chave foi fornecida
    if not api_key_header_value:
        raise UnauthorizedError(detail="Acesso negado: API Key ausente no cabecalho.")

    # Comparação segura contra Timing Attacks
    if secrets.compare_digest(api_key_header_value, settings.API_KEY):
        return api_key_header_value
    
    raise UnauthorizedError(detail="Acesso negado: API Key invalida.")

