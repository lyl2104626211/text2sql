from app.pojo.column_metric import ColumnMetricMysql
from app.service_pojo.column_metric_service_pojo import ColumnMetricServicePOJO


class ColumnMetricMapper:
    """字段-指标关联实体映射器"""

    @staticmethod
    def to_entity(service_pojo: ColumnMetricServicePOJO) -> ColumnMetricMysql:
        """
        将业务实体转换为数据实体

        Args:
            service_pojo: 业务实体对象

        Returns:
            数据实体对象
        """
        return ColumnMetricMysql(
            column_id=service_pojo.column_id,
            metric_id=service_pojo.metric_id
        )

    @staticmethod
    def to_service_pojo(entity: ColumnMetricMysql) -> ColumnMetricServicePOJO:
        """
        将数据实体转换为业务实体

        Args:
            entity: 数据实体对象

        Returns:
            业务实体对象
        """
        return ColumnMetricServicePOJO(
            column_id=entity.column_id,
            metric_id=entity.metric_id
        )

    @staticmethod
    def to_entity_list(service_pojos: list[ColumnMetricServicePOJO]) -> list[ColumnMetricMysql]:
        """批量将业务实体转换为数据实体"""
        return [ColumnMetricMapper.to_entity(pojo) for pojo in service_pojos]

    @staticmethod
    def to_service_pojo_list(entities: list[ColumnMetricMysql]) -> list[ColumnMetricServicePOJO]:
        """批量将数据实体转换为业务实体"""
        return [ColumnMetricMapper.to_service_pojo(entity) for entity in entities]