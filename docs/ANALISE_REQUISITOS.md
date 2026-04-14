# Análise de Requisitos - Sistema de Gestão de KPIs

**Versão:** 1.0  
**Data:** 2026-04-09  
**Status:** Em Definição  
**Projeto:** gestao_kpis_api  
**Empresa:** Matrix - Comercializadora de Energia Elétrica LTDA

---

## 1. Executive Summary

O projeto **gestao_kpis_api** é uma solução backend para centralizar e gerenciar Key Performance Indicators (KPIs) da Matrix. A API fornece operações CRUD para rastrear KPIs organizacionais, integrada ao BigQuery para análise de dados em larga escala, com suporte para múltiplos ambientes (desenvolvimento local e produção na Vercel).

---

## 2. Problem Statement

### O Problema
- **Atualmente:** Cada área de negócio gerencia KPIs de forma descentralizada, sem visibilidade holística
- **Impacto:** Falta de governança de dados, inconsistência nas métricas e dificuldade para tomar decisões estratégicas
- **Necessidade:** Plataforma centralizada e confiável para gestão e monitoramento de KPIs em tempo real

### Contexto do Negócio
Matrix é uma comercializadora de energia elétrica que opera em múltiplas áreas de negócio (Geração, Distribuição, Comercial, Risco, etc.). Cada área precisa monitorar e reportar KPIs críticos para:
- Compliance regulatório
- Tomada de decisão estratégica
- Avaliação de performance
- Análise comparativa entre áreas

---

## 3. Target Audience (Personas)

### 3.1 Gerentes de Operação (Priority: P0)
- **Role:** Acompanhamento diário de KPIs da sua área
- **Necessidades:** 
  - Visualizar KPIs atualizados em tempo real
  - Filtrar por período e área de negócio
  - Receber alertas quando KPIs desviarem de metas

### 3.2 Analistas de Dados (Priority: P0)
- **Role:** Governança e validação de dados
- **Necessidades:** 
  - Ingerir e validar dados de KPIs
  - Auditar histórico de mudanças
  - Exportar dados para análises avançadas

### 3.3 Executivos / C-Suite (Priority: P1)
- **Role:** Decisões estratégicas e reportes
- **Necessidades:** 
  - Dashboard executivo com KPIs agregados
  - Trend analysis e comparativos
  - Relatórios mensais/trimestrais

### 3.4 Integradores de Sistemas (Priority: P1)
- **Role:** Integração com sistemas existentes
- **Necessidades:** 
  - API RESTful bem documentada
  - Autenticação segura
  - Suporte a webhooks para notificações

---

## 4. Análise do Estado Atual

### 4.1 Arquitetura Existente
```
┌─────────────────┐
│   FastAPI       │
│   (main.py)     │
├─────────────────┤
│  Controllers    │
│  (kpi.py)       │
├─────────────────┤
│  Services       │
│  (kpi.py)       │
├─────────────────┤
│ SQLAlchemy ORM  │
├─────────────────┤
│  SQLite (dev)   │
│  BigQuery (prod)│
└─────────────────┘
```

### 4.2 Features Implementadas
- ✅ API REST básica para CRUD de KPIs
- ✅ Autenticação via API Key
- ✅ Suporte a BigQuery para data warehouse
- ✅ Deploy serverless na Vercel
- ✅ Data validation com Pydantic

### 4.3 Gaps Identificados
- ❌ Documentação de endpoints incompleta
- ❌ Sem tratamento robusto de erros por caso de uso
- ❌ Sem versionamento de dados (audit trail)
- ❌ Sem paginação em listagens
- ❌ Sem filtros avançados (período, área, responsável)
- ❌ Sem testes automatizados completos
- ❌ Sem logging centralizado
- ❌ Sem rate limiting
- ❌ Sem suporte a webhooks
- ❌ Sem modelagem de relacionamentos (áreas, responsáveis)

---

## 5. User Stories e Priorização

### 5.1 MVP (Must Have - Iteração 1)

#### US-001: Gerenciar KPI Básico
```
Como Analista de Dados,
Eu quero criar, ler, atualizar e deletar KPIs,
Para que eu possa manter a base de dados de KPIs atualizada.
```

**Priority:** P0  
**Acceptance Criteria:**
- [ ] POST /kpis - Criar novo KPI com validação
- [ ] GET /kpis - Listar todos os KPIs com paginação (limit, offset)
- [ ] GET /kpis/{id_kpi} - Recuperar KPI específico
- [ ] PUT /kpis/{id_kpi} - Atualizar KPI existente
- [ ] DELETE /kpis/{id_kpi} - Deletar KPI
- [ ] Validação de campos obrigatórios (area_negocio, nome_kpi, periodo_referencia)
- [ ] Validação de periodo_referencia (formato YYYY-MM-DD)
- [ ] Resposta padronizada com status HTTP correto

---

#### US-002: Filtrar KPIs por Critérios
```
Como Gerente de Operação,
Eu quero filtrar KPIs por área de negócio e período,
Para que eu possa visualizar apenas os KPIs relevantes da minha área.
```

**Priority:** P0  
**Acceptance Criteria:**
- [ ] Query parameter: ?area_negocio=valor
- [ ] Query parameter: ?periodo_referencia=2026-04-01 (maior ou igual)
- [ ] Query parameter: ?responsavel=nome
- [ ] Suporte a múltiplos filtros combinados (AND logic)
- [ ] Filtros opcionais não rompem a query se omitidos
- [ ] Performance: resposta < 500ms para 10k registros

---

#### US-003: Validar Integridade de Dados
```
Como Analista de Dados,
Eu quero saber quando dados inválidos são recebidos,
Para que eu possa corrigir problemas antes que afetem análises.
```

**Priority:** P0  
**Acceptance Criteria:**
- [ ] Rejeitação de KPI sem id_kpi
- [ ] Rejeitação de area_negocio vazia
- [ ] Rejeitação de periodo_referencia inválida
- [ ] Mensagens de erro claras e específicas (não genéricas)
- [ ] Código de erro HTTP apropriado (400 para validation)
- [ ] Exemplo: `{ "detail": [{"loc": ["body", "area_negocio"], "msg": "field required", "type": "value_error.missing"}] }`

---

#### US-004: Autenticar Requisições
```
Como Operador da Plataforma,
Eu quero que apenas usuários autorizados acessem a API,
Para que eu mantenha a segurança dos dados sensíveis.
```

**Priority:** P0  
**Acceptance Criteria:**
- [ ] Rejeitar requisições sem API Key
- [ ] Validar API Key em todas as rotas (exceto /docs e /)
- [ ] Retornar 401 Unauthorized para API Key inválida
- [ ] Suportar API Key via header X-API-Key

---

### 5.2 Importante (Should Have - Iteração 2)

#### US-005: Rastrear Alterações
```
Como Analista de Dados,
Eu quero saber quem alterou um KPI e quando,
Para que eu possa auditar mudanças críticas.
```

**Priority:** P1  
**Acceptance Criteria:**
- [ ] Campo created_at (timestamp imutável)
- [ ] Campo updated_at (timestamp atualizado a cada mudança)
- [ ] Campo updated_by (quem fez a última alteração)
- [ ] Tabela de histórico com todas as versões de KPI
- [ ] Endpoint GET /kpis/{id_kpi}/history para listar alterações

---

#### US-006: Suportar Notificações
```
Como Gerente de Operação,
Eu quero ser notificado quando um KPI é atualizado,
Para que eu fique ciente de mudanças importantes em tempo real.
```

**Priority:** P1  
**Acceptance Criteria:**
- [ ] Webhook POST para URL registrada on create/update/delete
- [ ] Payload inclui: evento, KPI anterior e novo, timestamp
- [ ] Retry automático com backoff exponencial
- [ ] Endpoint para registrar URLs de webhook
- [ ] Endpoint para listar webhooks cadastrados
- [ ] Timeout: 5 segundos por tentativa, max 3 tentativas

---

#### US-007: Documentação Interativa da API
```
Como Integrador de Sistemas,
Eu quero testar os endpoints da API no Swagger/OpenAPI,
Para que eu entenda exatamente como usar a API.
```

**Priority:** P1  
**Acceptance Criteria:**
- [ ] Endpoint /docs (Swagger UI) funcionando
- [ ] Endpoint /redoc (ReDoc) funcionando
- [ ] Todos os schemas documentados com exemplos
- [ ] Descrição clara de cada endpoint
- [ ] Exemplos de requisição e resposta
- [ ] Documentação de erros possíveis

---

### 5.3 Nice to Have (Could Have - Backlog)

#### US-008: Suportar Bulk Operations
```
Como Integrador de Sistemas,
Eu quero criar/atualizar múltiplos KPIs em uma única requisição,
Para que eu economize chamadas de API.
```

**Priority:** P2  
**Acceptance Criteria:**
- [ ] POST /kpis/bulk (lista de KPIs)
- [ ] PUT /kpis/bulk (lista de atualizações)
- [ ] Resposta com resultados parciais em caso de falha
- [ ] Limite: máximo 100 KPIs por requisição

---

#### US-009: Exportar Dados
```
Como Analista de Dados,
Eu quero exportar KPIs em CSV/JSON,
Para que eu possa analisar em ferramentas externas.
```

**Priority:** P2  
**Acceptance Criteria:**
- [ ] GET /kpis/export?format=csv
- [ ] GET /kpis/export?format=json
- [ ] Filtros aplicáveis (área, período)
- [ ] Limite de 10k linhas por exportação

---

#### US-010: Dashboard Inicial
```
Como Executivo,
Eu quero visualizar um dashboard com KPIs agregados,
Para que eu entenda a saúde geral do negócio.
```

**Priority:** P3  
**Acceptance Criteria:**
- [ ] Frontend (React/Next.js) simples com grid de KPIs
- [ ] Cards mostrando: nome, valor atual, meta, % de performance
- [ ] Indicador visual de status (🟢 green, 🟡 yellow, 🔴 red)
- [ ] Filtro por área de negócio
- [ ] Último período atualizado destaca em topo

---

## 6. Acceptance Criteria (Critérios de Aceitação Gerais)

### Funcionais
- Todos os endpoints retornam JSON válido
- Códigos HTTP são apropriados (200, 201, 400, 401, 404, 500)
- Respostas incluem estrutura consistente: `{ data: {...}, message: "string", timestamp: "ISO8601" }`
- Operações idempotentes funcionam corretamente (PUT)

### Não-Funcionais
- **Performance:** Resposta < 500ms (p95) para queries comuns
- **Confiabilidade:** 99.9% uptime em produção
- **Segurança:** Autenticação obrigatória, dados validados, sem SQL injection
- **Escalabilidade:** Suportar 10k QPS (query per second) via BigQuery
- **Observabilidade:** Logs estruturados, rastreamento de erros

### Qualidade de Código
- Cobertura de testes >= 80%
- Sem warnings do linter (black, flake8)
- Documentação de todos os públicos (docstrings)
- Type hints em 100% do código

---

## 7. Success Metrics

| Métrica | Target | Como Medir |
|---------|--------|-----------|
| **API Availability** | 99.9% | Monitoramento Vercel/CloudFlare |
| **Response Time (p95)** | < 500ms | APM logs |
| **Error Rate** | < 0.1% | Sentry/CloudTrail |
| **Test Coverage** | >= 80% | pytest --cov |
| **Documentation Completeness** | 100% endpoints | Manual review |
| **User Adoption** | 90% das áreas usando | Survey/analytics |

---

## 8. Technical Constraints & Assumptions

### Constraints
- **Servidor:** Vercel (serverless) - sem state local
- **Banco:** BigQuery em produção, SQLite em dev
- **Autenticação:** API Key no header
- **Performance:** Cold start < 3s

### Assumptions
- BigQuery já tem as tabelas criadas via dbt/console
- Todas as áreas têm acesso à VPN (se necessário)
- Período de referência é sempre menor ou igual a data atual

---

## 9. Out of Scope (WON'T)

- ❌ Frontend web completo (apenas API)
- ❌ Mobile app nativa (usar API web)
- ❌ Machine learning / previsões automáticas
- ❌ Integração com sistemas legados (ex: SAP)
- ❌ Multi-tenancy (uma instância por empresa)
- ❌ Suporte a time zones customizados (sempre UTC)
- ❌ Versionamento semântico de dados (apenas audit trail básico)
- ❌ Cache distribuído (Redis)

---

## 10. Roadmap de Iterações

### Iteração 1 (Sprint 1-2) - MVP
**Goal:** API funcional com CRUD básico
- [ ] US-001: CRUD de KPIs
- [ ] US-002: Filtros por área e período
- [ ] US-003: Validação de dados
- [ ] US-004: Autenticação via API Key
- [ ] US-007: Documentação no Swagger

**Deliverables:**
- API REST pronta para staging
- Testes unitários > 80%
- Documentação de endpoints

---

### Iteração 2 (Sprint 3-4) - Governança
**Goal:** Rastreabilidade e notificações
- [ ] US-005: Audit trail
- [ ] US-006: Webhooks
- [ ] Melhorias de erro handling

**Deliverables:**
- Histórico de alterações funcional
- Webhook integrado com 3 clientes piloto

---

### Iteração 3 (Sprint 5+) - Analytics & UX
**Goal:** Experiência completa de usuário
- [ ] US-008: Bulk operations
- [ ] US-009: Export de dados
- [ ] US-010: Dashboard básico

**Deliverables:**
- Dashboard MVP para 3 áreas piloto
- Exportação de relatórios

---

## 11. Referências

- **Repositório:** `gestao_kpis_api`
- **Tech Stack:** FastAPI, SQLAlchemy, BigQuery, Vercel
- **API Docs (ao vivo):** https://gestao-kpis-api.vercel.app/docs
- **Banco de Dados Schema:** `tb_kpis` com campos [id_kpi, area_negocio, nome_kpi, periodo_referencia, Responsavel, dados_kpi]

---

## 12. Próximos Passos

1. **Validação:** Revisão com stakeholders de cada área de negócio
2. **Refinamento:** Detalhar historias e acceptance criteria com times técnico e produto
3. **Estimativa:** Planning session para definir sprints e capacidade
4. **Execução:** Kickoff com desenvolvimento

---

**Documento preparado por:** Product Manager  
**Revisado em:** 2026-04-09  
**Próxima revisão:** Após kickoff da Iteração 1
