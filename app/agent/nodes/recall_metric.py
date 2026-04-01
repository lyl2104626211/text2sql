from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from app.prompt.prompt_loader import load_prompt
from langchain_core.output_parsers import  JsonOutputParser
from app.core.log import logger

from app.service_pojo import MetricServicePOJO


async def recall_metric(state:DataAgentState,runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回指标", "status": "running"})
    try:
        # 获取当前节点的输入
        query = state["query"]
        keywords = state["keywords"]
        # 使用大模型扩充关键词
        prompt_template = PromptTemplate(template=load_prompt("extend_keywords_for_metric_recall"),
                                         input_variables=["query"])
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        res = await chain.ainvoke({"query": query})
        # 合并关键词
        keywords = list(set(keywords + res))
        embedding_model = runtime.context["embedding_model"]
        metric_qdrant_repository = runtime.context["metric_qdrant_repository"]
        id_map: dict[str, MetricServicePOJO] = {}
        logger.info(f"扩充后的指标关键词：{keywords}")
        for keywords in keywords:
            # 向量化关键词
            embedding_text = await embedding_model.aembed_query(keywords)
            # 从向量数据库中搜素关键词
            current_metric_infos = await metric_qdrant_repository.search(embedding_text, limit=5)
            for metric_info in current_metric_infos:
                if metric_info.id not in id_map:
                    id_map[metric_info.id] = metric_info
        logger.info(f"搜索到指标信息：{list(id_map.keys())}")
        writer({"type": "progress", "step": "召回指标", "status": "success"})
        return {"retrieved_metric_infos": list(id_map.values())}
    except Exception as e:
        logger.error(f"召回指标失败：{e}")
        writer({"type": "progress", "step": "召回指标", "status": "error"})
        raise
