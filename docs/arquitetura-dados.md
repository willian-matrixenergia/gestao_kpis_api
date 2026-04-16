# Arquitetura de Dados — KPIs & Metas
## Brief para desenvolvimento de API

---

## Contexto

Sistema de gestão e acompanhamento de KPIs da Matrix Energy.
Os dados vivem no **BigQuery** e a API deve servir um dashboard em **Next.js**.

- **Projeto GCP:** `matrix-data-products-prd`
- **Dataset:** `ds_gestao_kpis`
- **Total de KPIs ativos:** 56
- **BUs cobertas:** Bitcoin, BESS, GD, GSII, Trading Gas, Trading Energia, Energia Fácil, Operações Estruturadas

---

## Modelo de dados

### Diagrama de relacionamentos

```
dim_kpi (master)
├── dim_regra_kpi      1 KPI → N regras (versionadas)
├── dim_meta           1 KPI → N metas (por periodicidade)
│    └── fct_meta_valor     1 meta → N targets históricos
└── fct_kpi_valor      1 KPI → N valores (1 por processamento)
      └── fct_kpi_variacao   1 valor → 1 variação vs processamento base
```

---

### Tabelas — estrutura completa

#### `dim_kpi` — cadastro master dos KPIs
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | STRING PK | Slug único ex: `gd_faturamento_gd` |
| `nm` | STRING | Nome do KPI |
| `nm_bu` | STRING | Business Unit (Bitcoin, BESS, GD…) |
| `nm_area` | STRING | Área dona (opcional) |
| `nm_responsavel` | STRING | Responsável(eis) |
| `nm_unidade` | STRING | Unidade de medida (MWh, R$ MM, %, GWh…) |
| `tp_periodicidade` | STRING | `Semanal` ou `Mensal` |
| `tp_relatorio` | STRING | `Executivo` ou `Operacional` |
| `dt_criacao` | DATE | — |
| `fl_ativo` | BOOL | Flag de ativo |

#### `dim_regra_kpi` — regras de cálculo versionadas
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | STRING PK | ex: `regra_gd_faturamento_gd` |
| `fk_pk_id_kpi` | STRING FK → dim_kpi | — |
| `fk_pk_id_regra_anterior` | STRING FK → dim_regra_kpi | Encadeia versões. NULL na primeira |
| `ds` | STRING | Descrição da fórmula/lógica |
| `dt_criacao` | DATE | — |
| `fl_ativo` | BOOL | Apenas 1 regra ativa por KPI |

#### `dim_meta` — cadastro das metas
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | STRING PK | ex: `meta_gd_faturamento_gd` |
| `fk_pk_id_kpi` | STRING FK → dim_kpi | — |
| `nm_meta` | STRING | Nome descritivo |
| `nm_bu` | STRING | BU da meta (pode diferir do KPI) |
| `nm_area` | STRING | — |
| `dt_criacao` | DATE | — |
| `tp_meta` | STRING | `Semanal` ou `Mensal` — sempre igual ao `tp_periodicidade` do KPI |

#### `fct_kpi_valor` — valores realizados (append-only)
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | STRING PK | ID do processamento ex: `PROC-2026-04-GD_FATUR-0001` |
| `fk_pk_id_kpi` | STRING FK → dim_kpi | — |
| `fk_pk_id_regra` | STRING FK → dim_regra_kpi | Regra usada neste cálculo |
| `vl` | FLOAT64 | Valor apurado |
| `dt_referencia` | DATE | Competência (partição) |
| `dt_processamento` | DATETIME | Timestamp da execução |
| `nm_responsavel` | STRING | Quem rodou |

> **Importante:** nunca há UPDATE. Cada reprocessamento insere nova linha.
> A view `vw_kpi_ultimo_valor` deduplica e entrega sempre o mais recente.

#### `fct_kpi_variacao` — variações entre processamentos
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | STRING PK | — |
| `fk_pk_processamento` | STRING FK → fct_kpi_valor | Processamento resultado |
| `fk_pk_processamento_base` | STRING FK → fct_kpi_valor | Processamento base da comparação |
| `vl_variacao_abs` | FLOAT64 | resultado - base |
| `vl_variacao_pct` | FLOAT64 | (resultado - base) / base × 100 |
| `dt_referencia` | DATE | Competência (partição) |

#### `fct_meta_valor` — histórico de targets
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | STRING PK | — |
| `fk_pk_id_meta` | STRING FK → dim_meta | — |
| `vl_meta` | FLOAT64 | Valor do target |
| `dt_referencia` | DATE | Competência (partição) |
| `dt_cadastro` | DATETIME | Inserção original |
| `dt_atualizacao` | DATETIME | Revisão mais recente |
| `nm_responsavel_atualizacao` | STRING | Quem revisou |

---

## Views prontas para API

### `vw_kpi_ultimo_valor` — **view principal, usar como fonte primária**

Entrega por linha: último valor realizado de cada KPI por competência,
com todos os atributos enriquecidos e indicadores já calculados.

**Campos disponíveis:**

```
id_processamento        — ID do processamento mais recente
id_kpi                  — ID do KPI
nm_kpi                  — Nome
nm_bu                   — Business Unit
nm_area                 — Área
nm_responsavel_kpi      — Responsável do KPI
nm_unidade              — Unidade de medida (usar para formatar valor no frontend)
tp_periodicidade        — Semanal | Mensal
tp_relatorio            — Executivo | Operacional
fl_kpi_ativo            — boolean

id_regra                — ID da regra aplicada
ds_regra                — Descrição da fórmula usada
fl_regra_ativa          — boolean

vl_realizado            — Valor apurado
dt_referencia           — Competência
dt_processamento        — Quando foi calculado
nm_responsavel_calculo  — Quem executou

id_meta                 — ID da meta
nm_meta                 — Nome da meta
tp_meta                 — Tipo da meta
vl_meta                 — Target vigente
dt_atualizacao_meta     — Quando o target foi revisado
nm_responsavel_meta     — Quem revisou o target

pct_atingimento         — FLOAT (0–100+). Ex: 94.3 = 94.3%
vl_gap_absoluto         — vl_realizado - vl_meta
status_atingimento      — 'atingido' | 'atencao' | 'critico' | 'sem_meta'
```

**Regra de status:**
- `atingido` → pct_atingimento >= 100
- `atencao`  → pct_atingimento >= 80
- `critico`  → pct_atingimento < 80
- `sem_meta` → vl_meta IS NULL

---

## Endpoints sugeridos para a API

### `GET /kpis`
Lista todos os KPIs com último valor da competência mais recente.

```sql
SELECT *
FROM `matrix-data-products-prd.ds_gestao_kpis.vw_kpi_ultimo_valor`
WHERE fl_kpi_ativo = TRUE
  AND dt_referencia = (
    SELECT MAX(dt_referencia)
    FROM `matrix-data-products-prd.ds_gestao_kpis.vw_kpi_ultimo_valor`
  )
ORDER BY nm_bu, nm_kpi;
```

**Query params sugeridos:** `bu`, `tp_relatorio`, `status_atingimento`, `tp_periodicidade`

---

### `GET /kpis/:id`
Detalhe de um KPI com histórico dos últimos 6 meses.

```sql
SELECT *
FROM `matrix-data-products-prd.ds_gestao_kpis.vw_kpi_ultimo_valor`
WHERE id_kpi = @id_kpi
ORDER BY dt_referencia DESC
LIMIT 6;
```

---

### `GET /kpis/:id/variacao`
Evolução mês a mês com variação calculada.

```sql
SELECT
  k.nm                  AS nm_kpi,
  res.dt_referencia,
  res.vl                AS vl_resultado,
  base.vl               AS vl_base,
  var.vl_variacao_abs,
  var.vl_variacao_pct
FROM `matrix-data-products-prd.ds_gestao_kpis.fct_kpi_variacao`   var
JOIN `matrix-data-products-prd.ds_gestao_kpis.fct_kpi_valor`      res  ON res.id  = var.fk_pk_processamento
JOIN `matrix-data-products-prd.ds_gestao_kpis.fct_kpi_valor`      base ON base.id = var.fk_pk_processamento_base
JOIN `matrix-data-products-prd.ds_gestao_kpis.dim_kpi`            k    ON k.id    = res.fk_pk_id_kpi
WHERE k.id = @id_kpi
ORDER BY res.dt_referencia DESC;
```

---

### `GET /dashboard/summary`
Agregado por BU para o header do dashboard.

```sql
SELECT
  nm_bu,
  COUNT(*)                                    AS total_kpis,
  COUNTIF(status_atingimento = 'atingido')    AS atingidos,
  COUNTIF(status_atingimento = 'atencao')     AS em_atencao,
  COUNTIF(status_atingimento = 'critico')     AS criticos,
  COUNTIF(status_atingimento = 'sem_meta')    AS sem_meta,
  ROUND(AVG(pct_atingimento), 1)              AS media_pct_atingimento
FROM `matrix-data-products-prd.ds_gestao_kpis.vw_kpi_ultimo_valor`
WHERE fl_kpi_ativo = TRUE
  AND dt_referencia = (
    SELECT MAX(dt_referencia)
    FROM `matrix-data-products-prd.ds_gestao_kpis.vw_kpi_ultimo_valor`
  )
GROUP BY nm_bu
ORDER BY nm_bu;
```

---

## Regras de negócio importantes para a API

1. **Nunca fazer UPDATE** em `fct_kpi_valor` — cada reprocessamento é um INSERT novo.
   A deduplicação é feita pela view via `MAX(dt_processamento)`.

2. **`nm_unidade`** deve ser usado pelo frontend para formatar o valor:
   - `%` → exibir como percentual
   - `R$ MM` → formatar em milhões de reais
   - `MWh`, `GWh`, `kWh` → energia
   - `BTC`, `USD`, `R$/MWh`, `R$/m3` → moeda/preço

3. **Queries sempre parametrizadas** — nunca interpolar strings em SQL
   (usar `@param` no BigQuery client ou `?` dependendo do driver).

4. **Particionamento** — todas as fatos são particionadas por `dt_referencia`.
   Sempre incluir filtro de data nas queries para evitar full scan.

5. **`status_atingimento`** já vem calculado na view — não recalcular no backend.

---

## Stack de acesso recomendada

- **Client BigQuery:** `@google-cloud/bigquery` (Node.js) com autenticação via Service Account
- **Autenticação:** Application Default Credentials (ADC) ou chave JSON da SA com role `BigQuery Data Viewer`
- **Cache:** considerar cache de 5–15min nos endpoints de listagem (dados não mudam em tempo real)
 