from typing import TypedDict, NotRequired, Required, Optional

from app.service_pojo import MetricServicePOJO, ColumnServicePOJO
from app.service_pojo.value_info_service_pojo import ValueInfo


class MetricInfoState(TypedDict):
    name: str  # 指标名称
    alias: list[str]  # 指标别名
    relevant_columns: list[str]  # 关联字段列表
    description: str  # 指标描述


class DateInfoState(TypedDict):
    date: str
    weekday: str
    quarter: str


class DBInfoState(TypedDict):
    dialect: str
    version: str


class ColumnInfoState(TypedDict):
    name: str  # 字段名称
    type: str  # 数据类型
    role: str  # 字段类型(primary_key,foreign_key,measure,dimension)
    description: str  # 字段描述
    alias: list[str]  # 字段别名
    examples: list[str]  # 字段的示例值


class TableInfoState(TypedDict):
    name: str  # 表名称
    role: str  # 表角色
    description: str  # 表描述
    columns: list[ColumnInfoState]  # 字段信息


class DataAgentState(TypedDict, total=False):
    query: Required[str]  # 存储用户输入的查询
    error: Optional[str]  # 存储数据库的错误信息
    keywords: Optional[list[str]]  # 存储抽取的关键词
    retrieved_column_infos: Optional[list[ColumnServicePOJO]]  # 存储召回的字段信息
    retrieved_metric_infos: Optional[list[MetricServicePOJO]]  # 存储召回的指标信息
    retrieved_value_infos: Optional[list[ValueInfo]]  # 存储召回的字段取值信息
    table_infos: Optional[list[TableInfoState]]  # 存储表信息
    metric_infos: Optional[list[MetricInfoState]]  # 存储指标信息
    date_info_state: Optional[DateInfoState]  # 存储日期信息
    db_info_state: Optional[DBInfoState]  # 存储数据库信息
    sql: Optional[str]  # 存储生成的SQL
