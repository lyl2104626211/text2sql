from app.pojo.column_info import ColumnInfoMysql
from app.service_pojo.column_service_pojo import ColumnServicePOJO


class ColumnMapper:
    """字段信息实体映射器"""

    @staticmethod
    def to_entity(service_pojo: ColumnServicePOJO) -> ColumnInfoMysql:
        """
        将业务实体转换为数据实体

        Args:
            service_pojo: 业务实体对象

        Returns:
            数据实体对象
        """
        return ColumnInfoMysql(
            id=service_pojo.id,
            name=service_pojo.name,
            type=service_pojo.type,
            role=service_pojo.role,
            examples=service_pojo.examples,
            description=service_pojo.description,
            alias=service_pojo.alias,
            table_id=service_pojo.table_id
        )

    @staticmethod
    def to_service_pojo(entity: ColumnInfoMysql) -> ColumnServicePOJO:
        """
        将数据实体转换为业务实体

        Args:
            entity: 数据实体对象

        Returns:
            业务实体对象
        """
        return ColumnServicePOJO(
            id=entity.id,
            name=entity.name,
            type=entity.type,
            role=entity.role,
            examples=entity.examples,
            description=entity.description,
            alias=entity.alias,
            table_id=entity.table_id
        )

    @staticmethod
    def to_entity_list(service_pojos: list[ColumnServicePOJO]) -> list[ColumnInfoMysql]:
        """批量将业务实体转换为数据实体"""
        return [ColumnMapper.to_entity(pojo) for pojo in service_pojos]

    @staticmethod
    def to_service_pojo_list(entities: list[ColumnInfoMysql]) -> list[ColumnServicePOJO]:
        """批量将数据实体转换为业务实体"""
        return [ColumnMapper.to_service_pojo(entity) for entity in entities]