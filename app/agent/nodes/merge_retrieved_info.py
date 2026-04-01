from app.agent import state
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, ColumnInfoState, TableInfoState, MetricInfoState
from langgraph.runtime import Runtime

from app.pojo.table_info import TableInfoMysql
from app.service_pojo import ColumnServicePOJO


async def merge_retrieved(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    """
    合并召回信息节点

    该节点负责整合来自多个召回源（指标、字段、字段值）的信息，并按表进行分组组织。
    主要处理逻辑：
        1. 将指标关联的字段合并到总字段集合中
        2. 将字段的候选值添加到字段的examples列表中
        3. 按表分组字段信息，构建完整的表结构
        4. 转换为最终的状态格式返回

    Args:
        state: 数据代理状态，包含召回的指标信息、字段信息、字段值信息
        runtime: LangGraph运行时上下文，提供流写入器和依赖仓库

    Returns:
        包含table_infos（表信息列表）和metric_infos（指标信息列表）的字典
    """
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "合并召回信息", "status": "running"})
    try:
        retrieved_value_infos = state["retrieved_value_infos"]
        retrieved_metric_infos = state["retrieved_metric_infos"]
        retrieved_column_infos = state["retrieved_column_infos"]
        meta_mysql_repository = runtime.context["meta_mysql_repository"]

        # 构建字段ID到字段对象的映射字典，用于快速查找和去重
        colum_infos_id_map: dict[str, ColumnServicePOJO] = {column_info.id: column_info for column_info in
                                                            retrieved_column_infos}

        # -----------------------------------------------------------
        # 步骤1：补充指标关联但未在召回结果中的字段
        # 遍历所有召回的指标，将其关联的字段添加到总字段集合
        # -----------------------------------------------------------
        for metric_info in retrieved_metric_infos:
            for relevant_column in metric_info.relevant_columns:
                # 检查该字段是否已存在于映射中
                if relevant_column not in colum_infos_id_map:
                    # 若不存在，则从DW数据库查询完整的字段信息并添加
                    column_info: ColumnServicePOJO = await meta_mysql_repository.get_column_by_id(relevant_column)
                    colum_infos_id_map[relevant_column] = column_info

        # -----------------------------------------------------------
        # 步骤2：为字段填充候选值（examples）
        # 将召回的字段值信息添加到对应字段的examples列表中
        # -----------------------------------------------------------
        for value_info in retrieved_value_infos:
            # 若字段尚未在映射中，先查询完整信息
            if value_info.column_id not in colum_infos_id_map:
                column_info: ColumnServicePOJO = await meta_mysql_repository.get_column_by_id(value_info.column_id)
                colum_infos_id_map[column_info.id] = column_info
            # 将候选值添加到字段的examples列表（避免重复）
            if value_info.value not in colum_infos_id_map[value_info.column_id].examples:
                colum_infos_id_map[value_info.column_id].examples.append(value_info.value)

        # -----------------------------------------------------------
        # 步骤3：按表分组，构建表结构
        # 将字段按所属表进行分组，便于后续SQL生成
        # -----------------------------------------------------------
        map_table_columns: dict[str, list[ColumnServicePOJO]] = {}
        for column_info in colum_infos_id_map.values():
            if column_info.table_id not in map_table_columns:
                map_table_columns[column_info.table_id] = []
            map_table_columns[column_info.table_id].append(column_info)

        # 为每个表强制添加主外键信息
        for table_id, column_infos in map_table_columns.items():
            key_columns = await meta_mysql_repository.get_column_by_key_type(table_id)
            column_ids = [column_info.id for column_info in column_infos]
            for column_info in key_columns:
                if column_info.id not in column_ids:
                    map_table_columns[table_id].append(column_info)



        # -----------------------------------------------------------
        # 步骤4：构建表信息列表
        # 为每个表查询完整信息，并将字段列表包装成状态对象
        # -----------------------------------------------------------
        tables_state: list[TableInfoState] = []
        for table_id, column_infos in map_table_columns.items():
            # 将字段对象转换为字段状态对象
            columns_state = [ColumnInfoState(
                name=column_info.name,
                type=column_info.type,
                role=column_info.role,
                description=column_info.description,
                alias=column_info.alias,
                examples=column_info.examples,
            ) for column_info in column_infos]
            # 查询表的完整元信息
            table_info: TableInfoMysql = await meta_mysql_repository.get_table_info_by_id(table_id)
            # 构建表状态对象并添加到列表
            table_info_state = TableInfoState(name=table_info.name, role=table_info.role,
                                              description=table_info.description,
                                              columns=columns_state)
            tables_state.append(table_info_state)

        # -----------------------------------------------------------
        # 步骤5：构建指标信息列表
        # 将召回的指标信息转换为状态格式
        # -----------------------------------------------------------
        metric_infos: list[MetricInfoState] = [MetricInfoState(
            name=metric_info.name,
            alias=metric_info.alias,
            description=metric_info.description,
            relevant_columns=metric_info.relevant_columns
        ) for metric_info in retrieved_metric_infos]

        writer({"type": "progress", "step": "合并召回信息", "status": "success"})
        return {"table_infos": tables_state, "metric_infos": metric_infos}
    except Exception as e:
        logger.error(f"合并召回信息失败：{e}")
        writer({"type": "progress", "step": "合并召回信息", "status": "error"})
        raise
