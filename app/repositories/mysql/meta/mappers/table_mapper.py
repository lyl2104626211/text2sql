from app.pojo.table_info import TableInfoMysql
from app.service_pojo.table_service_pojo import TableServicePOJO


class TableMapper:
    """表信息实体映射器"""

    @staticmethod
    def to_entity(service_pojo: TableServicePOJO) -> TableInfoMysql:
        """
        将业务实体转换为数据实体

        Args:
            service_pojo: 业务实体对象

        Returns:
            数据实体对象
        """
        return TableInfoMysql(
            id=service_pojo.id,
            name=service_pojo.name,
            role=service_pojo.role,
            description=service_pojo.description
        )

    @staticmethod
    def to_service_pojo(entity: TableInfoMysql) -> TableServicePOJO:
        """
        将数据实体转换为业务实体

        Args:
            entity: 数据实体对象

        Returns:
            业务实体对象
        """
        return TableServicePOJO(
            id=entity.id,
            name=entity.name,
            role=entity.role,
            description=entity.description
        )

    @staticmethod
    def to_entity_list(service_pojos: list[TableServicePOJO]) -> list[TableInfoMysql]:
        """批量将业务实体转换为数据实体"""
        return [TableMapper.to_entity(pojo) for pojo in service_pojos]

    @staticmethod
    def to_service_pojo_list(entities: list[TableInfoMysql]) -> list[TableServicePOJO]:
        """批量将数据实体转换为业务实体"""
        return [TableMapper.to_service_pojo(entity) for entity in entities]