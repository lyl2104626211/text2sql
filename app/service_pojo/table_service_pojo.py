from dataclasses import dataclass
from typing import Optional


@dataclass
class TableServicePOJO:
    """
    表信息服务层实体类

    用于在服务层传递表元数据，不直接关联数据库ORM
    """
    id: str  # 表编号，唯一标识
    name: Optional[str] = None  # 表名称
    role: Optional[str] = None  # 表类型(fact/dim)
    description: Optional[str] = None  # 表描述
