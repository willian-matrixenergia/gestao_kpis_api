# Plano de Resolução de Gaps - Sistema de Gestão de KPIs

**Versão:** 1.0  
**Data:** 2026-04-09  
**Baseado em:** ANALISE_REQUISITOS.md  
**Responsável:** Product Manager + Tech Lead

---

## Overview

Este documento detalha como resolver os 10 gaps identificados na análise atual, priorizados por **impacto no negócio** e **esforço técnico**.

---

## 1. Matriz de Priorização

```
                     IMPACTO ALTO
                          ↑
     ┌──────────────────────┼──────────────────────┐
     │                      │                      │
     │  QUICK WINS          │   STRATEGIC          │
     │  (Fazer já!)         │   (Investir tempo)   │
     │                      │                      │
     │  Gap-01: Docs        │  Gap-03: Audit Trail │
     │  Gap-02: Errors      │  Gap-10: Relations   │
     │  Gap-06: Rate limit  │                      │
     │                      │                      │
     ├──────────────────────┼──────────────────────┤
     │                      │                      │
     │  LOW PRIORITY        │   TECHNICAL DEBT     │
     │  (Backlog)           │   (Sprint 5+)        │
     │                      │                      │
     │  Gap-08: Webhooks    │  Gap-07: Logging     │
     │  Gap-09: Relacionam  │  Gap-04: Paginação  │
     │                      │  Gap-05: Filtros    │
     │                      │                      │
     └──────────────────────┼──────────────────────┘
                            ↓
                      IMPACTO BAIXO
                ESFORÇO ALTO →
```

---

## 2. Detalhamento dos Gaps e Plano de Ação

### 🟢 QUICK WINS (Iteração 1 - Sprint 1)

---

#### Gap-01: Documentação de Endpoints Incompleta

**Impacto:** ALTO - Bloqueia integradores de sistemas  
**Esforço:** BAIXO - 2-3 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
- Swagger/ReDoc não documentam os campos corretamente
- Faltam exemplos de request/response
- Erros possíveis não são documentados
- Sem descritivo de query parameters

**Solução:**
```python
# Exemplo: adicionar no endpoint GET /kpis
@router.get(
    "/",
    response_model=List[KpiResponse],
    summary="Listar KPIs",
    description="Retorna lista paginada de KPIs com suporte a filtros",
    tags=["KPIs"],
    responses={
        200: {
            "description": "Lista de KPIs",
            "content": {
                "application/json": {
                    "example": {
                        "data": [{
                            "id_kpi": "KPI-001",
                            "area_negocio": "Geração",
                            "nome_kpi": "Disponibilidade",
                            "periodo_referencia": "2026-04-01",
                            "Responsavel": "João Silva",
                            "dados_kpi": {"valor": 98.5, "meta": 99.0}
                        }],
                        "message": "Sucesso",
                        "timestamp": "2026-04-09T14:30:00Z"
                    }
                }
            }
        },
        400: {"description": "Query parameters inválidos"},
        401: {"description": "API Key ausente ou inválida"},
        500: {"description": "Erro interno do servidor"}
    }
)
def list_kpis(
    skip: int = Query(0, description="Número de registros a pular", ge=0),
    limit: int = Query(10, description="Limite de registros por página", ge=1, le=100),
    area_negocio: Optional[str] = Query(None, description="Filtrar por área"),
    db: Session = Depends(get_db)
) -> dict:
    """Retorna lista paginada de KPIs."""
    pass
```

**Tarefas:**
- [ ] Adicionar docstrings em todos os endpoints
- [ ] Definir exemplos de sucesso (200, 201)
- [ ] Documentar respostas de erro (400, 401, 404, 500)
- [ ] Adicionar Field descriptions em Pydantic schemas
- [ ] Criar documento ENDPOINT_SPEC.md com matriz de compatibilidade
- [ ] Validar no Swagger/ReDoc após mudanças

**Entrega:**
- `/docs` completo e testado
- Documento de API reference em Markdown
- Exemplos cURL para cada endpoint

---

#### Gap-02: Tratamento Robusto de Erros

**Impacto:** ALTO - Afeta UX de integradores  
**Esforço:** MÉDIO - 3-4 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
```json
// Erro genérico (ruim)
{
  "detail": "An error occurred"
}

// Deveria ser específico (bom)
{
  "error_code": "VALIDATION_ERROR",
  "message": "Campo 'area_negocio' é obrigatório",
  "details": {
    "field": "area_negocio",
    "expected_type": "string",
    "received": null
  },
  "timestamp": "2026-04-09T14:30:00Z",
  "request_id": "req-12345"
}
```

**Solução:**
```python
# core/exceptions.py
class KpiException(Exception):
    """Base exception para erros de negócio"""
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

class ValidationError(KpiException):
    pass

class NotFoundError(KpiException):
    pass

class DuplicateError(KpiException):
    pass

# main.py
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

**Mapa de Erros:**

| HTTP | Caso | Error Code | Exemplo |
|------|------|-----------|---------|
| 400 | Campo obrigatório faltando | `VALIDATION_ERROR` | area_negocio vazio |
| 400 | Formato de data inválido | `INVALID_DATE_FORMAT` | periodo_referencia="abc" |
| 401 | API Key ausente | `MISSING_API_KEY` | Header X-API-Key não enviado |
| 401 | API Key inválida | `INVALID_API_KEY` | Chave expirada ou incorreta |
| 404 | KPI não encontrado | `KPI_NOT_FOUND` | GET /kpis/inexistente |
| 409 | ID_KPI já existe | `DUPLICATE_KPI` | POST com id duplicado |
| 429 | Rate limit excedido | `RATE_LIMIT_EXCEEDED` | Muitas requisições |
| 500 | Erro no banco de dados | `DATABASE_ERROR` | Falha ao conectar BigQuery |
| 500 | Erro desconhecido | `INTERNAL_ERROR` | Bug no código |

**Tarefas:**
- [ ] Criar módulo `core/exceptions.py` com classes de erro
- [ ] Implementar exception handlers para cada tipo
- [ ] Adicionar request_id para rastreamento
- [ ] Documentar error codes no Swagger
- [ ] Criar teste para cada erro possível
- [ ] Adicionar logging de erros para debugger

**Entrega:**
- Error handling definido e testado
- Documento de códigos de erro
- Testes cobrindo happy path e sad paths

---

#### Gap-06: Rate Limiting

**Impacto:** ALTO - Protege infraestrutura  
**Esforço:** MÉDIO - 2-3 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
- Sem proteção contra abuso
- Sem limite por API Key
- Sem throttling

**Solução:**
```python
# utils/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# main.py
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)

# controllers/kpi.py
@router.get("/")
@limiter.limit("100/minute")  # 100 requests por minuto
def list_kpis(request: Request, ...):
    """Lista KPIs"""
    pass
```

**Limites Propostos:**
- **Leitura (GET):** 100 req/minuto por API Key
- **Escrita (POST/PUT):** 10 req/minuto por API Key
- **Deleção (DELETE):** 5 req/minuto por API Key
- **Bulk operations:** 2 req/minuto por API Key

**Tarefas:**
- [ ] Instalar `slowapi` ou similar
- [ ] Implementar rate limiter por API Key (não por IP)
- [ ] Configurar limites por tipo de operação
- [ ] Adicionar headers X-RateLimit-* nas respostas
- [ ] Testes de rate limiting
- [ ] Dashboard para monitorar excesso de requisições

**Entrega:**
- Rate limiting ativo e funcional
- Documentação de limites públicos
- Alerts configurados para anomalias

---

### 🟡 STRATEGIC (Iteração 2-3 - Sprint 2-4)

---

#### Gap-03: Versionamento de Dados (Audit Trail)

**Impacto:** ALTO - Crítico para compliance  
**Esforço:** ALTO - 5-7 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
- Sem histórico de mudanças
- Impossível saber quem alterou o quê
- Sem rollback de alterações

**Solução Arquitetural:**
```python
# models/kpi_audit.py
class KpiAudit(Base):
    """Registro de auditoria - histórico completo"""
    __tablename__ = "tb_kpis_audit"
    
    id_audit = Column(Integer, primary_key=True, autoincrement=True)
    id_kpi = Column(String(255), ForeignKey("tb_kpis.id_kpi"))
    
    # Snapshot do estado anterior
    data_anterior = Column(JSONEncodedDict)
    # Snapshot do estado novo
    data_nova = Column(JSONEncodedDict)
    
    # Metadados da mudança
    operacao = Column(String(50))  # CREATE, UPDATE, DELETE
    usuario = Column(String(255))  # Quem fez
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    motivo = Column(String(500), nullable=True)  # Por que

# Modelo principal (tb_kpis) com metadata
class Kpi(Base):
    __tablename__ = "tb_kpis"
    
    id_kpi = Column(String(255), primary_key=True)
    # ... campos normais ...
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255), nullable=True)
    
    is_deleted = Column(Boolean, default=False)  # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(255), nullable=True)
```

**Endpoints Novos:**
```
GET /kpis/{id_kpi}/history
    - Retorna todas as versões do KPI com timestamps
    - Query params: ?limit=50&skip=0

GET /kpis/{id_kpi}/history/{version_id}
    - Retorna específica versão
    
POST /kpis/{id_kpi}/rollback
    - Restaura para versão anterior
    - Body: { "target_version": "2026-04-08T10:30:00Z", "reason": "Erro de entrada" }
```

**Tarefas:**
- [ ] Criar tabela `tb_kpis_audit` no BigQuery
- [ ] Adicionar campos metadata em `tb_kpis`
- [ ] Criar modelo Pydantic `KpiAudit`
- [ ] Interceptor/middleware para capturar mudanças
- [ ] Endpoints de history e rollback
- [ ] Testes de auditoria
- [ ] Dashboard de auditoria

**Entrega:**
- Audit trail completo e funcional
- Capacidade de rollback
- Relatório de auditoria para compliance

---

#### Gap-10: Modelagem de Relacionamentos

**Impacto:** ALTO - Estrutura fundamental  
**Esforço:** ALTO - 6-8 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
- `area_negocio` e `Responsavel` são apenas strings
- Sem validação de valores válidos
- Sem relacionamentos entre entidades

**Solução:**
```python
# models/area.py
class AreaNegocio(Base):
    __tablename__ = "tb_areas_negocio"
    
    id_area = Column(String(50), primary_key=True)
    nome = Column(String(255), unique=True)
    descricao = Column(String(500))
    gerente_geral = Column(String(255))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# models/responsavel.py
class Responsavel(Base):
    __tablename__ = "tb_responsaveis"
    
    id_responsavel = Column(String(50), primary_key=True)
    nome_completo = Column(String(255))
    email = Column(String(255), unique=True)
    id_area = Column(String(50), ForeignKey("tb_areas_negocio.id_area"))
    cargo = Column(String(255))
    telefone = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True)
    
    # Relacionamento
    area = relationship("AreaNegocio")

# models/kpi.py (ATUALIZADO)
class Kpi(Base):
    __tablename__ = "tb_kpis"
    
    id_kpi = Column(String(255), primary_key=True)
    id_area = Column(String(50), ForeignKey("tb_areas_negocio.id_area"))
    id_responsavel = Column(String(50), ForeignKey("tb_responsaveis.id_responsavel"))
    nome_kpi = Column(String(255))
    periodo_referencia = Column(String(10))  # YYYY-MM
    dados_kpi = Column(JSONEncodedDict)
    
    # Relacionamentos
    area = relationship("AreaNegocio")
    responsavel = relationship("Responsavel")
```

**Schemas Pydantic:**
```python
class AreaNegocioResponse(BaseModel):
    id_area: str
    nome: str
    descricao: str
    ativo: bool

class ResponsavelResponse(BaseModel):
    id_responsavel: str
    nome_completo: str
    email: str
    cargo: str
    area: AreaNegocioResponse

class KpiResponse(BaseModel):
    id_kpi: str
    nome_kpi: str
    periodo_referencia: str
    dados_kpi: Dict[str, Any]
    area: AreaNegocioResponse
    responsavel: ResponsavelResponse
```

**Novos Endpoints:**
```
GET/POST   /areas
GET/PUT    /areas/{id_area}
GET/POST   /responsaveis
GET/PUT    /responsaveis/{id_responsavel}
GET        /responsaveis?id_area={id_area}
```

**Tarefas:**
- [ ] Criar modelos `AreaNegocio` e `Responsavel`
- [ ] Migração: mapear strings para IDs
- [ ] Endpoints CRUD para áreas e responsáveis
- [ ] Validações de integridade referencial
- [ ] Testes de relacionamentos
- [ ] Documentação da hierarquia

**Entrega:**
- Modelo de dados relacional
- CRUD de áreas e responsáveis
- Validação de integridade

---

### 🔵 TECHNICAL DEBT (Iteração 3+ - Sprint 3+)

---

#### Gap-04: Paginação em Listagens

**Impacto:** MÉDIO - UX e performance  
**Esforço:** MÉDIO - 3-4 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
```python
# Ruim: sem paginação
@router.get("/")
def list_kpis(db: Session):
    return db.query(Kpi).all()  # Retorna TUDO!
```

**Solução:**
```python
# schemas/pagination.py
class PaginationParams(BaseModel):
    skip: int = Query(0, ge=0, description="Quantos registros pular")
    limit: int = Query(10, ge=1, le=100, description="Máx 100 registros")

class PaginatedResponse(BaseModel):
    data: List[Any]
    pagination: dict = {
        "skip": int,
        "limit": int,
        "total": int,
        "pages": int,
        "current_page": int
    }

# controllers/kpi.py
@router.get("/", response_model=PaginatedResponse)
def list_kpis(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(Kpi).count()
    kpis = db.query(Kpi).offset(skip).limit(limit).all()
    return {
        "data": kpis,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
            "current_page": (skip // limit) + 1
        }
    }
```

**Tarefas:**
- [ ] Criar classe `PaginatedResponse`
- [ ] Atualizar todos os GET /list
- [ ] Adicionar testes de paginação
- [ ] Documentar parâmetros no Swagger

**Entrega:**
- Paginação funcional
- Testes de limite de registro

---

#### Gap-05: Filtros Avançados

**Impacto:** MÉDIO - Usabilidade  
**Esforço:** MÉDIO - 3-4 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
```python
# Sem filtros
GET /kpis  # Retorna tudo
```

**Solução:**
```python
@router.get("/")
def list_kpis(
    area_negocio: Optional[str] = Query(None),
    periodo_referencia: Optional[str] = Query(None),  # >= desta data
    responsavel: Optional[str] = Query(None),
    nome_kpi: Optional[str] = Query(None),  # Contains (like)
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    query = db.query(Kpi)
    
    if area_negocio:
        query = query.filter(Kpi.area_negocio == area_negocio)
    if periodo_referencia:
        query = query.filter(Kpi.periodo_referencia >= periodo_referencia)
    if responsavel:
        query = query.filter(Kpi.Responsavel.contains(responsavel))
    if nome_kpi:
        query = query.filter(Kpi.nome_kpi.ilike(f"%{nome_kpi}%"))
    
    total = query.count()
    kpis = query.offset(skip).limit(limit).all()
    
    return {"data": kpis, "total": total}

# Exemplos
GET /kpis?area_negocio=Geração
GET /kpis?periodo_referencia=2026-01-01&area_negocio=Comercial
GET /kpis?nome_kpi=Disponibilidade
GET /kpis?area_negocio=Geração&skip=10&limit=20
```

**Tarefas:**
- [ ] Adicionar query parameters de filtro
- [ ] Implementar filtros no SQL
- [ ] Testes de combinação de filtros
- [ ] Validar performance com múltiplos filtros
- [ ] Documentar filtros no Swagger

**Entrega:**
- Filtros funcionais e performáticos
- Exemplos de queries comuns

---

#### Gap-07: Logging Centralizado

**Impacto:** MÉDIO - Observabilidade  
**Esforço:** MÉDIO - 3-5 dias  
**Status:** 🔴 Não iniciado

**Problema Atual:**
- Sem logs estruturados
- Sem rastreamento de requests
- Impossível debugar em produção

**Solução:**
```python
# core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# main.py
import logging
from core.logging import JSONFormatter

# Configurar logging estruturado
logging.basicConfig(level=logging.INFO)
formatter = JSONFormatter()
for handler in logging.root.handlers:
    handler.setFormatter(formatter)

logger = logging.getLogger(__name__)

# Middleware para rastrear requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    logger.info(f"Request started", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host
    })
    
    response = await call_next(request)
    
    logger.info(f"Request completed", extra={
        "request_id": request_id,
        "status_code": response.status_code,
        "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
    })
    
    return response
```

**Integração com Sentry:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)
```

**Tarefas:**
- [ ] Implementar JSON formatter
- [ ] Middleware de logging de requests
- [ ] Integração com Sentry/similar
- [ ] Logs estruturados em exceções
- [ ] Request ID em todos os logs
- [ ] Dashboard de logs

**Entrega:**
- Logging estruturado ativo
- Rastreamento de requests end-to-end
- Integração com ferramenta de APM

---

#### Gap-08: Suporte a Webhooks

**Impacto:** MÉDIO - Integrações  
**Esforço:** ALTO - 6-8 dias  
**Status:** 🔴 Não iniciado

**Solução:**
```python
# models/webhook.py
class Webhook(Base):
    __tablename__ = "tb_webhooks"
    
    id_webhook = Column(String(50), primary_key=True)
    url = Column(String(500), unique=True)
    eventos = Column(JSONEncodedDict)  # {"create": true, "update": true, "delete": false}
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)

# models/webhook_log.py
class WebhookLog(Base):
    __tablename__ = "tb_webhook_logs"
    
    id_log = Column(String(50), primary_key=True)
    id_webhook = Column(String(50), ForeignKey("tb_webhooks.id_webhook"))
    evento = Column(String(50))  # create, update, delete
    payload = Column(JSONEncodedDict)
    status_code = Column(Integer)
    resposta = Column(String(1000), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# services/webhook.py
async def disparar_webhook(evento: str, kpi_antes: dict, kpi_depois: dict):
    webhooks = db.query(Webhook).filter(
        Webhook.ativo == True,
        Webhook.eventos[evento] == True
    )
    
    for webhook in webhooks:
        payload = {
            "evento": evento,
            "timestamp": datetime.utcnow().isoformat(),
            "data_antes": kpi_antes,
            "data_nova": kpi_depois
        }
        
        # Disparo com retry
        async with httpx.AsyncClient(timeout=5.0) as client:
            for tentativa in range(3):
                try:
                    response = await client.post(webhook.url, json=payload)
                    log_webhook(webhook.id, evento, payload, response.status_code)
                    break
                except Exception as e:
                    if tentativa == 2:
                        log_webhook(webhook.id, evento, payload, 500, str(e))
                    else:
                        await asyncio.sleep(2 ** tentativa)  # Backoff exponencial

# Endpoints
POST   /webhooks          - Registrar webhook
GET    /webhooks          - Listar webhooks
PUT    /webhooks/{id}     - Atualizar
DELETE /webhooks/{id}     - Deletar
GET    /webhooks/{id}/logs - Ver histórico de disparos
```

**Tarefas:**
- [ ] Criar modelos `Webhook` e `WebhookLog`
- [ ] Endpoints CRUD de webhooks
- [ ] Sistema de disparo async
- [ ] Retry com backoff exponencial
- [ ] Log de tentativas
- [ ] Testes de webhook
- [ ] Dashboard de webhook health

**Entrega:**
- Webhooks funcionais
- Retry automático
- Visibilidade de status

---

#### Gap-09: Relacionamentos Avançados

**Impacto:** BAIXO - Nice to have  
**Esforço:** ALTO - 5-7 dias  
**Status:** 🔴 Não iniciado

**Exemplos:**
- Meta associada a KPI
- Alertas quando KPI desvia de meta
- Histórico de targets

**Tarefas (backlog):**
- [ ] Modelo de Meta
- [ ] Endpoints de CRUD
- [ ] Sistema de alertas
- [ ] Notificações por email/Slack

**Entrega:**
- Modelo de meta implementado
- Sistema de alertas básico

---

## 3. Matriz de Esforço vs. Impacto

### Resumo Executivo

| Gap | Descrição | Impacto | Esforço | Sprint | P/S |
|-----|-----------|---------|---------|--------|-----|
| 01 | Docs | ⚠️ ALTO | ✅ BAIXO | 1 | P0 |
| 02 | Errors | ⚠️ ALTO | ⚠️ MÉDIO | 1 | P0 |
| 06 | Rate Limit | ⚠️ ALTO | ⚠️ MÉDIO | 1 | P0 |
| 03 | Audit Trail | ⚠️ ALTO | 🔴 ALTO | 2 | P1 |
| 10 | Relacionamentos | ⚠️ ALTO | 🔴 ALTO | 2 | P1 |
| 04 | Paginação | 🟡 MÉDIO | ⚠️ MÉDIO | 2 | P1 |
| 05 | Filtros | 🟡 MÉDIO | ⚠️ MÉDIO | 2 | P1 |
| 07 | Logging | 🟡 MÉDIO | ⚠️ MÉDIO | 3 | P2 |
| 08 | Webhooks | 🟡 MÉDIO | 🔴 ALTO | 3 | P2 |
| 09 | Relacionam. | 🔵 BAIXO | 🔴 ALTO | 4+ | P3 |

---

## 4. Timeline de Entregas

```
Sprint 1 (1-2 semanas)        Sprint 2 (2-3 semanas)
├─ Gap-01: Docs              ├─ Gap-03: Audit Trail
├─ Gap-02: Errors            ├─ Gap-10: Relacionamentos
├─ Gap-06: Rate Limit        ├─ Gap-04: Paginação
└─ ✅ MVP Robusto            ├─ Gap-05: Filtros
                             └─ ✅ Governança & Usabilidade

Sprint 3 (2-3 semanas)        Sprint 4+ (Roadmap)
├─ Gap-07: Logging           ├─ Gap-09: Relacionamentos avançados
├─ Gap-08: Webhooks          ├─ Dashboard
├─ Melhorias de perf         ├─ Mobile
└─ ✅ Enterprise Ready       └─ 🚀 Produto Completo
```

---

## 5. Critérios de Sucesso por Sprint

### Sprint 1 ✅
- [ ] API documentada 100% (Swagger + Markdown)
- [ ] Todos erros mapeados e com mensagens claras
- [ ] Rate limiting ativo (100 req/min para GET)
- [ ] 0 breaking changes na API
- [ ] 80%+ test coverage

### Sprint 2 ✅
- [ ] Audit trail implementado e auditado
- [ ] Relacionamentos AreaNegocio/Responsavel funcionais
- [ ] Paginação em todas listagens
- [ ] Filtros por 4+ critérios
- [ ] Performance: <200ms (p95) para queries comuns

### Sprint 3 ✅
- [ ] Logging estruturado em produção
- [ ] Webhooks disparando sem falhas
- [ ] SLA: 99.9% uptime
- [ ] Documentação de operações completa

---

## 6. Checklist de Implementação

Use este checklist para rastrear progresso:

```markdown
## Sprint 1

### Gap-01: Documentação
- [ ] Adicionar descrições em todos endpoints
- [ ] Exemplos de success (200, 201)
- [ ] Exemplos de erro (400, 401, 404, 500)
- [ ] Swagger rodando perfeito
- [ ] Validar no /docs
- [ ] Validar no /redoc
- [ ] Documentação em Markdown pronto
- [ ] Code review aprovado

### Gap-02: Tratamento de Erros
- [ ] Criar core/exceptions.py
- [ ] Exception handlers para cada tipo
- [ ] Request ID em resposta
- [ ] Testes de erro (happy + sad path)
- [ ] Documentação de error codes
- [ ] Code review aprovado
- [ ] Deploy para staging

### Gap-06: Rate Limiting
- [ ] Instalar slowapi
- [ ] Configurar limites por tipo
- [ ] Testes de rate limit
- [ ] Headers X-RateLimit-*
- [ ] Monitoramento de exceções
- [ ] Code review aprovado
- [ ] Deploy para staging

### Validação Sprint 1
- [ ] Todos os critérios acima ✅
- [ ] Merge para main
- [ ] Deploy em staging
- [ ] Smoke tests em staging
```

---

## 7. Recursos e Responsabilidades

| Gap | Dev Backend | Dev Frontend | QA | DevOps | Líder |
|-----|------------|-------------|-----|--------|-------|
| 01 | 80% | - | 20% | - | Review |
| 02 | 100% | - | - | - | Review |
| 03 | 100% | - | - | - | Review |
| 04 | 100% | - | - | - | Review |
| 05 | 100% | - | - | - | Review |
| 06 | 70% | - | 30% | - | Review |
| 07 | 70% | - | - | 30% | Review |
| 08 | 100% | - | - | - | Review |
| 09 | 100% | - | - | - | Review |
| 10 | 100% | - | - | - | Review |

---

## 8. Riscos e Mitigação

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|----------------|-----------|
| BigQuery mudanças de schema | ALTO | BAIXA | Versionamento de migrations |
| Performance com audit trail | MÉDIO | MÉDIA | Índices + particionamento |
| Webhook flods externo | MÉDIO | MÉDIA | Rate limit + timeout + DLQ |
| API key exposure | ALTO | BAIXA | Rotação de chaves + Audit log |

---

## 9. Próximos Passos

1. **Aprovação:** Apresentar este plano ao Tech Lead e Product Owner
2. **Planning:** Detalhar user stories para Sprint 1
3. **Estimativa:** Estimar story points
4. **Kickoff:** Começar Sprint 1 na próxima segunda
5. **Tracking:** Daily standup para monitorar progresso

---

**Documento preparado por:** Product Manager + Tech Lead  
**Data:** 2026-04-09  
**Próxima revisão:** Após Sprint 1 (1-2 semanas)
