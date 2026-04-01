from dataclasses import dataclass
from typing import Optional


@dataclass
class ColumnServicePOJO:
    """
    字段信息服务层实体类

    用于在服务层传递字段元数据，不直接关联数据库ORM
    """
    id: str                              # 列编号，唯一标识：表名.字段名
    name: Optional[str] = None           # 列名称
    type: Optional[str] = None           # 数据类型
    role: Optional[str] = None           # 列类型(primary_key,foreign_key,measure,dimension)
    examples: Optional[list[str]] = None  # 数据示例
    alias: Optional[list[str]] = None  # 列别名
    description: Optional[str] = None   # 列描述
    table_id: Optional[str] = None        # 所属表编号