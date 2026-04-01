import asyncio

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from app.repositories.es.value_repository import ValueESRepository
from app.client.es_client_manager import es_manager
from app.agent.context import DataAgentContext
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.run_sql import run_sql
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.merge_retrieved_info import merge_retrieved
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.validate_sql import validate_sql
from app.agent.state import DataAgentState
from app.client.emdding_client_manager import embedding_manager
from app.client.qdrant_client_manager import qdrant_manager
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.client.mysql_client_manager import db_meta_manager
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.client.mysql_client_manager import db_dw_manager

graph_builder = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)

# 添加节点
graph_builder.add_node("extract_keywords", extract_keywords)
graph_builder.add_node("recall_column", recall_column)
graph_builder.add_node("recall_value", recall_value)
graph_builder.add_node("recall_metric", recall_metric)
graph_builder.add_node("merge_retrieved_info", merge_retrieved)
graph_builder.add_node("filter_metric", filter_metric)
graph_builder.add_node("filter_table", filter_table)
graph_builder.add_node("add_extra_context", add_extra_context)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("validate_sql", validate_sql)
graph_builder.add_node("correct_sql", correct_sql)
graph_builder.add_node("run_sql", run_sql)

# 添加关系
graph_builder.add_edge(START, "extract_keywords")
graph_builder.add_edge("extract_keywords", "recall_column")
graph_builder.add_edge("extract_keywords", "recall_value")
graph_builder.add_edge("extract_keywords", "recall_metric")
graph_builder.add_edge("recall_column", "merge_retrieved_info")
graph_builder.add_edge("recall_value", "merge_retrieved_info")
graph_builder.add_edge("recall_metric", "merge_retrieved_info")
graph_builder.add_edge("merge_retrieved_info", "filter_table")
graph_builder.add_edge("merge_retrieved_info", "filter_metric")
graph_builder.add_edge("filter_table", "add_extra_context")
graph_builder.add_edge("filter_metric", "add_extra_context")
graph_builder.add_edge("add_extra_context", "generate_sql")
graph_builder.add_edge("generate_sql", "validate_sql")

graph_builder.add_conditional_edges("validate_sql",
                                    lambda state: "run_sql" if state["error"] is None else "correct_sql", {
                                        "correct_sql": "correct_sql",
                                        "run_sql": "run_sql"
                                    })

graph_builder.add_edge("correct_sql", "run_sql")
graph_builder.add_edge("run_sql", END)

# 打印图结构（文本形式）
graph_compile = graph_builder.compile()
if __name__ == '__main__':
    async def main():
        state = DataAgentState(query="统计华北地区的2025年第一季度的销售总额")
        qdrant_manager.init()
        es_manager.init()
        db_meta_manager.init()
        db_dw_manager.init()
        async with (db_meta_manager.session_factory() as db_meta_session,
                    db_dw_manager.session_factory() as db_dw_session):
            column_qdrant_repository = ColumnQdrantRepository(qdrant_manager.client)
            metric_qdrant_repository = MetricQdrantRepository(qdrant_manager.client)
            value_es_repository = ValueESRepository(es_manager.client)
            meta_mysql_repository = MetaMysqlRepository(db_meta_session)
            dw_mysql_repository = DwMysqlRepository(db_dw_session)
            embedding_manager.init()
            context = DataAgentContext(column_qdrant_repository=column_qdrant_repository,
                                       embedding_model=embedding_manager.client,
                                       metric_qdrant_repository=metric_qdrant_repository,
                                       value_es_repository=value_es_repository,
                                       meta_mysql_repository=meta_mysql_repository,
                                       dw_mysql_repository=dw_mysql_repository)
            async for chunk in graph_compile.astream(input=state, context=context, stream_mode='custom'):
                print(chunk)
        await qdrant_manager.close()
        await es_manager.close()
        await db_meta_manager.close()
        await db_dw_manager.close()


    asyncio.run(main())
