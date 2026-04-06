"""
Testes de autenticação via API Key.
Valida os 3 cenários de segurança: chave válida, inválida e ausente.
"""
import pytest
from fastapi.testclient import TestClient
from core.config import settings
from main import app

client = TestClient(app)

VALID_KEY = settings.API_KEY
INVALID_KEY = "chave_errada_12345"


class TestRootEndpointAuth:
    """Testes de autenticação no endpoint raiz (/)."""

    def test_root_with_valid_key(self):
        """Requisição com chave válida deve retornar 200."""
        response = client.get("/", headers={settings.API_KEY_NAME: VALID_KEY})
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_root_with_invalid_key(self):
        """Requisição com chave inválida deve retornar 403."""
        response = client.get("/", headers={settings.API_KEY_NAME: INVALID_KEY})
        assert response.status_code == 403
        assert "inválida" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()

    def test_root_without_key(self):
        """Requisição sem chave deve retornar 403."""
        response = client.get("/")
        assert response.status_code == 403
        assert "ausente" in response.json()["detail"].lower() or "missing" in response.json()["detail"].lower()


class TestKpiEndpointAuth:
    """Testes de autenticação nos endpoints de KPIs."""

    def test_kpis_with_valid_key(self):
        """GET /kpis com chave válida deve retornar 200."""
        response = client.get("/kpis/", headers={settings.API_KEY_NAME: VALID_KEY})
        assert response.status_code == 200

    def test_kpis_with_invalid_key(self):
        """GET /kpis com chave inválida deve retornar 403."""
        response = client.get("/kpis/", headers={settings.API_KEY_NAME: INVALID_KEY})
        assert response.status_code == 403

    def test_kpis_without_key(self):
        """GET /kpis sem chave deve retornar 403."""
        response = client.get("/kpis/")
        assert response.status_code == 403

    def test_post_kpi_without_key(self):
        """POST /kpis sem chave deve retornar 403."""
        response = client.post("/kpis/", json={"id_kpi": "TST-001", "nome": "Teste"})
        assert response.status_code == 403


class TestSecurityHeaders:
    """Testes de robustez da validação de segurança."""

    def test_empty_key_is_rejected(self):
        """Chave vazia deve ser rejeitada."""
        response = client.get("/", headers={settings.API_KEY_NAME: ""})
        assert response.status_code == 403

    def test_key_is_case_sensitive(self):
        """A chave é case-sensitive."""
        response = client.get("/", headers={settings.API_KEY_NAME: VALID_KEY.upper()})
        # Só passa se a chave original não for toda maiúscula
        if VALID_KEY != VALID_KEY.upper():
            assert response.status_code == 403

    def test_wrong_header_name_is_rejected(self):
        """Header com nome errado deve ser rejeitado."""
        response = client.get("/", headers={"Authorization": VALID_KEY})
        assert response.status_code == 403
