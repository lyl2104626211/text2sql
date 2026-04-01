from dataclasses import dataclass
from typing import Optional


@dataclass
class MetricServicePOJO:
    """
    指标信息服务层实体类

    用于在服务层传递指标元数据，不直接关联数据库ORM
    """
    id: str  # 指标编码，唯一标识
    name: Optional[str] = None  # 指标名称
    description: Optional[str] = None  # 指标描述
    relevant_columns: Optional[list[str]] = None  # 关联字段列表，存储字段ID如 "fact_order.order_amount"
    alias: Optional[list[str]] = None            # 指标别名

