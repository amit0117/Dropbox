from __future__ import annotations

from supabase import Client, create_client
from postgrest import APIError

from app.core.config import AppConfig
from app.models.enums import SupabaseOperatorType
from app.utils.logger import logger
from app.utils.singleton import SingletonMeta


class DBClient(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.supabase: Client = None
        self._initialise_client()

    def _initialise_client(self) -> None:
        try:
            config = AppConfig()
            self.supabase = create_client(config.supabase_url, config.supabase_key)
            logger.info("Supabase DB client initialised successfully.")
        except Exception as exc:
            logger.error("Failed to initialise Supabase DB client: %s", exc)
            raise

    def insert_row(self, table_name: str, data: dict) -> dict:
        response = self.supabase.table(table_name).insert(data).execute()
        return response.data[0]

    def get_single_row(self, table_name: str, *columns: str, where_condition_dict: dict | None = None) -> dict | None:
        select_columns = columns if columns else ("*",)
        query = self.supabase.table(table_name).select(*select_columns)
        query = self._apply_conditions(query, where_condition_dict)

        result = query.maybe_single().execute()
        return result.data if result else None

    def get_rows(
        self,
        table_name: str,
        *columns: str,
        where_condition_dict: dict | None = None,
        order_by_columns: list | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> tuple[list[dict], int]:
        try:
            select_columns = columns if columns else ("*",)
            query = self.supabase.table(table_name).select(*select_columns, count="exact")

            query = self._apply_conditions(query, where_condition_dict)

            if order_by_columns:
                for column, is_desc in order_by_columns:
                    query = query.order(column, desc=is_desc)

            if limit is not None:
                if skip is not None:
                    query = query.range(skip, skip + limit - 1)
                else:
                    query = query.limit(limit)
            elif skip is not None:
                query = query.offset(skip)

            result = query.execute()
            return result.data, result.count

        except APIError as api_err:
            if api_err.code == "PGRST103":
                return [], 0
            raise

    def update_row(self, table_name: str, data: dict, where_condition_dict: dict) -> dict | None:
        query = self.supabase.table(table_name).update(data)
        query = self._apply_conditions(query, where_condition_dict)
        response = query.execute()
        return response.data[0] if response.data else None

    def delete_row(
        self,
        table_name: str,
        where_condition_dict: dict,
    ) -> None:
        query = self.supabase.table(table_name).delete()
        query = self._apply_conditions(query, where_condition_dict)
        query.execute()

    @staticmethod
    def _apply_conditions(query, where_condition_dict: dict | None):
        if not where_condition_dict:
            return query
        for column, (operator, value) in where_condition_dict.items():
            if operator == SupabaseOperatorType.IS_NOT_NULL.value:
                query = query.not_.is_(column, None)
            else:
                query = getattr(query, operator)(column, value)
        return query
