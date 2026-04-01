from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.pojo.column_info import ColumnInfoMysql
from app.pojo.metric_info import MetricInfo
from app.pojo.table_info import TableInfoMysql
from app.repositories.mysql.meta.mappers import TableMapper, ColumnMapper, MetricMapper, ColumnMetricMapper
from app.service_pojo import TableServicePOJO, ColumnServicePOJO, MetricServicePOJO, ColumnMetricServicePOJO
from sqlalchemy import text


class MetaMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_metric(self, metric: MetricInfo) -> None:
        """
        添加单个指标信息到数据库

        Args:
            metric: 指标信息对象
        """
        self.session.add(metric)
        await self.session.commit()

    async def add_metrics(self, metrics: list[MetricInfo]) -> None:
        """
        批量添加指标信息到数据库

        Args:
            metrics: 指标信息对象列表
        """
        for metric in metrics:
            self.session.add(metric)
        await self.session.commit()

    def save_tables(self, table_infos: list[TableServicePOJO]) -> None:
        """
        批量保存表信息到数据库

        Args:
            table_infos: 表信息对象列表
        """
        self.session.add_all([TableMapper.to_entity(table) for table in table_infos])

    def save_columns(self, column_infos: list[ColumnServicePOJO]) -> None:
        """
        批量保存字段信息到数据库

        Args:
            column_infos: 字段信息对象列表
        """
        self.session.add_all([ColumnMapper.to_entity(column) for column in column_infos])

    def save_metrics(self, metric_infos: list[MetricServicePOJO]) -> None:
        """
        批量保存指标信息到数据库

        Args:
            metric_infos: 指标信息对象列表
        """
        self.session.add_all([MetricMapper.to_entity(metric) for metric in metric_infos])

    def save_column_metrics(self, column_metric_infos: list[ColumnMetricServicePOJO]) -> None:
        """
        批量保存字段-指标关联关系到数据库

        Args:
            column_metric_infos: 字段-指标关联关系对象列表
        """
        self.session.add_all([ColumnMetricMapper.to_entity(cm) for cm in column_metric_infos])

    async def get_column_info_by_id(self, column_id: int) -> ColumnServicePOJO | None:
        column_info: ColumnInfoMysql | None = await self.session.get(ColumnInfoMysql, column_id)
        if column_info:
            return ColumnMapper.to_service_pojo(column_info)
        return None

    async def get_table_info_by_id(self, table_id: int) -> TableServicePOJO | None:
        table_info: TableInfoMysql | None = await self.session.get(TableInfoMysql, table_id)
        if table_info:
            return TableMapper.to_service_pojo(table_info)
        return None

    async def get_column_by_key_type(self, table_id: str)->list[ColumnServicePOJO]:
        sql = f"select * from column_info where table_id='{table_id}' and role in ('primary_key','foreign_key')"
        res = await self.session.execute(text(sql))
        return [ColumnServicePOJO(**dict(row)) for row in res.mappings().fetchall()]
