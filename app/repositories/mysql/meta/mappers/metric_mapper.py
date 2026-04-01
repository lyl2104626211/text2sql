from app.pojo.metric_info import MetricInfo
from app.service_pojo.metric_service_pojo import MetricServicePOJO


class MetricMapper:
    """指标信息实体映射器"""

    @staticmethod
    def to_entity(service_pojo: MetricServicePOJO) -> MetricInfo:
        """
        将业务实体转换为数据实体

        Args:
            service_pojo: 业务实体对象

        Returns:
            数据实体对象
        """
        return MetricInfo(
            id=service_pojo.id,
            name=service_pojo.name,
            description=service_pojo.description,
            relevant_columns=service_pojo.relevant_columns,
            alias=service_pojo.alias
        )

    @staticmethod
    def to_service_pojo(entity: MetricInfo) -> MetricServicePOJO:
        """
        将数据实体转换为业务实体

        Args:
            entity: 数据实体对象

        Returns:
            业务实体对象
        """
        return MetricServicePOJO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            relevant_columns=entity.relevant_columns,
            alias=entity.alias
        )

    @staticmethod
    def to_entity_list(service_pojos: list[MetricServicePOJO]) -> list[MetricInfo]:
        """批量将业务实体转换为数据实体"""
        return [MetricMapper.to_entity(pojo) for pojo in service_pojos]

    @staticmethod
    def to_service_pojo_list(entities: list[MetricInfo]) -> list[MetricServicePOJO]:
        """批量将数据实体转换为业务实体"""
        return [MetricMapper.to_service_pojo(entity) for entity in entities]