from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from app.agent.llm import llm
from langchain_core.prompts import PromptTemplate
from app.prompt.prompt_loader import load_prompt
from langchain_core.output_parsers import JsonOutputParser
from app.core.log import logger

from app.service_pojo import ColumnServicePOJO


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段", "status": "running"})
    try:
        keywords = state["keywords"]
        query = state["query"]
        # 用大模型扩充关键词
        prompt_template = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"),
                                         input_variables=["query"])
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        res = await chain.ainvoke({"query": query})
        keywords = list(set(keywords + res))
        embedding_model = runtime.context["embedding_model"]
        column_qdrant_repository = runtime.context["column_qdrant_repository"]
        id_map: dict[str, ColumnServicePOJO] = {}
        logger.info(f"扩充后的字段关键词：{keywords}")
        for keywords in keywords:
            # 向量化关键字
            embedding_text = await embedding_model.aembed_query(keywords)
            # 从向量数据库中搜素关键字
            current_columns_infos = await column_qdrant_repository.search(embedding_text, limit=5)
            for column_info in current_columns_infos:
                if column_info.id not in id_map:
                    id_map[column_info.id] = column_info
        logger.info(f"搜索的字段信息：{list(id_map.keys())}")
        writer({"type": "progress", "step": "召回字段", "status": "success"})
        return {"retrieved_column_infos": list(id_map.values())}
    except Exception as e:
        logger.error(f"召回字段失败：{e}")
        writer({"type": "progress", "step": "召回字段", "status": "error"})
        raise
