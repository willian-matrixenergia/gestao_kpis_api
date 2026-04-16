from datetime import datetime, timezone


class KpiApiError(Exception):
    """Exceção base para erros de negócio da API de KPIs."""

    def __init__(self, code: str, message: str, status_code: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "message": self.message,
            "details": self.details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class NotFoundError(KpiApiError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} com id '{resource_id}' nao encontrado.",
            status_code=404,
            details={"resource": resource, "id": resource_id},
        )


class DuplicateError(KpiApiError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="DUPLICATE",
            message=f"{resource} com id '{resource_id}' ja existe.",
            status_code=409,
            details={"resource": resource, "id": resource_id},
        )


class DatabaseError(KpiApiError):
    def __init__(self, operation: str, detail: str = ""):
        super().__init__(
            code="DATABASE_ERROR",
            message=f"Erro no banco de dados durante '{operation}'.",
            status_code=500,
            details={"operation": operation, "detail": detail},
        )


class UnauthorizedError(KpiApiError):
    def __init__(self, detail: str = "Acesso negado: API Key ausente ou invalida."):
        super().__init__(
            code="UNAUTHORIZED",
            message=detail,
            status_code=401,
        )
