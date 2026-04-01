from dataclasses import dataclass


@dataclass
class ColumnMetricServicePOJO:
    """
    字段-指标关联关系服务层实体类

    用于在服务层传递字段与指标的关联关系，不直接关联数据库ORM
    """
    column_id: str  # 列编号
    metric_id: str  # 指标编号
