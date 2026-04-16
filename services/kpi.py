from typing import Optional, List, Dict, Any

from google.cloud import bigquery

from core.config import settings


class KpiBigQueryService:
    """
    Service read-only que consulta a view vw_kpi_ultimo_valor no BigQuery.
    Todos os valores são retornados como strings para manter compatibilidade
    com o formato flat do JSON de integração.
    """

    VIEW_NAME = "vw_kpi_ultimo_valor"

    def __init__(self):
        self._table_ref = f"`{settings.BIGQUERY_TABLE_PREFIX}.{self.VIEW_NAME}`"

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def get_all(
        self,
        client: bigquery.Client,
        *,
        id_kpi: Optional[str] = None,
        nm_bu_kpi: Optional[str] = None,
        nm_area_kpi: Optional[str] = None,
        dt_referencia: Optional[str] = None,
        status_atingimento: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Lista registros da view com filtros opcionais e paginacao."""
        conditions: List[str] = []
        params: List[bigquery.ScalarQueryParameter] = []

        if id_kpi:
            conditions.append("id_kpi = @id_kpi")
            params.append(bigquery.ScalarQueryParameter("id_kpi", "STRING", id_kpi))

        if nm_bu_kpi:
            conditions.append("nm_bu = @nm_bu")
            params.append(bigquery.ScalarQueryParameter("nm_bu", "STRING", nm_bu_kpi))

        if nm_area_kpi:
            conditions.append("nm_area = @nm_area")
            params.append(bigquery.ScalarQueryParameter("nm_area", "STRING", nm_area_kpi))

        if dt_referencia:
            conditions.append("dt_referencia = @dt_referencia")
            params.append(bigquery.ScalarQueryParameter("dt_referencia", "STRING", dt_referencia))

        if status_atingimento:
            conditions.append("status_atingimento = @status_atingimento")
            params.append(bigquery.ScalarQueryParameter("status_atingimento", "STRING", status_atingimento))

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Query de contagem
        count_sql = f"SELECT COUNT(*) as total FROM {self._table_ref} {where_clause}"
        print(f"Executing query: {count_sql}")
        total = self._execute_scalar(client, count_sql, params)

        # Query de dados com paginação
        data_sql = (
            f"SELECT * FROM {self._table_ref} "
            f"{where_clause} "
            f"ORDER BY dt_processamento DESC "
            f"LIMIT @limit OFFSET @skip"
        )
        page_params = params + [
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("skip", "INT64", skip),
        ]

        rows = self._execute_query(client, data_sql, page_params)

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": rows,
        }

    def get_by_processamento(
        self,
        client: bigquery.Client,
        id_processamento: str,
    ) -> Optional[Dict[str, Any]]:
        """Busca um registro unico pelo id_processamento."""
        sql = (
            f"SELECT * FROM {self._table_ref} "
            f"WHERE id_processamento = @id_processamento "
            f"LIMIT 1"
        )
        params = [
            bigquery.ScalarQueryParameter("id_processamento", "STRING", id_processamento),
        ]
        rows = self._execute_query(client, sql, params)
        return rows[0] if rows else None

    def get_by_kpi(
        self,
        client: bigquery.Client,
        id_kpi: str,
    ) -> List[Dict[str, Any]]:
        """Busca todos os registros (historico) de um KPI especifico."""
        sql = (
            f"SELECT * FROM {self._table_ref} "
            f"WHERE id_kpi = @id_kpi "
            f"ORDER BY dt_processamento DESC"
        )
        params = [
            bigquery.ScalarQueryParameter("id_kpi", "STRING", id_kpi),
        ]
        return self._execute_query(client, sql, params)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _execute_query(
        self,
        client: bigquery.Client,
        sql: str,
        params: List[bigquery.ScalarQueryParameter],
    ) -> List[Dict[str, Any]]:
        """Executa uma query no BigQuery e retorna lista de dicts com todos os valores como string."""
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        query_job = client.query(sql, job_config=job_config)
        results = query_job.result()

        rows = []
        for row in results:
            row_dict = {}
            for key, value in row.items():
                # Converte tudo para string para manter o formato flat do JSON
                row_dict[key] = str(value) if value is not None else None
            rows.append(row_dict)
        return rows

    def _execute_scalar(
        self,
        client: bigquery.Client,
        sql: str,
        params: List[bigquery.ScalarQueryParameter],
    ) -> int:
        """Executa uma query que retorna um valor escalar (usado para COUNT)."""
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        query_job = client.query(sql, job_config=job_config)
        results = query_job.result()
        for row in results:
            return row[0]
        return 0


kpi_service = KpiBigQueryService()
