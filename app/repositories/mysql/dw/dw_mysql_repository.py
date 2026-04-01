from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.pojo.column_info import ColumnInfoMysql
from app.repositories.mysql.meta.mappers import ColumnMapper
from app.service_pojo import ColumnServicePOJO


class DwMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_columns(self, table_name: str) -> dict:
        """获取表的所有列名和类型"""
        query = text(f"SHOW COLUMNS FROM {table_name}")
        result = await self.session.execute(query)
        rows = result.mappings().fetchall()
        return {row["Field"]: row["Type"] for row in rows}

    async def get_column_values(self, table_name: str, column_name: str, limit: int = 5) -> list:
        """
        获取指定列的示例值

        Args:
            table_name: 表名
            column_name: 列名
            limit: 返回数量，默认5条

        Returns:
            列的示例值列表
        """
        query = text(f"""
            SELECT DISTINCT {column_name}
            FROM {table_name}
            WHERE {column_name} IS NOT NULL
            LIMIT :limit
        """)
        result = await self.session.execute(query, {"limit": limit})
        rows = result.mappings().fetchall()
        return [row[column_name] for row in rows]

    async def get_db_info(self):
        sql = 'select version()'
        result = await self.session.execute(text(sql))
        version = result.scalar()
        dialect = self.session.bind.dialect.name
        return {"dialect": dialect, "version": version}

    async def validate_sql(self, sql: str):
        sql = f"EXPLAIN {sql}"
        await self.session.execute(text(sql))
    async def run_sql(self, sql: str):
        result = await self.session.execute(text(sql))
        rows = result.mappings().fetchall()
        return [dict(row) for row in rows]