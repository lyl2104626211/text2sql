from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt
from app.service_pojo.value_info_service_pojo import ValueInfo


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段取值", "status": "running"})
    try:
        keywords = state["keywords"]
        query = state["query"]
        # 用大模型扩充关键词
        prompt_template = PromptTemplate(template=load_prompt("extend_keywords_for_value_recall"),
                                         input_variables=["query"])
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        res = await chain.ainvoke({"query": query})
        keywords = list(set(keywords + res))
        value_es_repository = runtime.context["value_es_repository"]
        id_map: dict[str, ValueInfo] = {}
        logger.info(f"扩充后的字段取值关键词：{keywords}")
        for keywords in keywords:
            # es全文搜索字段取值
            values = await value_es_repository.search(keywords)
            for value in values:
                if value.id not in id_map:
                    id_map[value.id] = value
        logger.info(f"搜索的字段取值信息：{list(id_map.keys())}")
        writer({"type": "progress", "step": "召回字段取值", "status": "success"})
        return {"retrieved_value_infos": list(id_map.values())}
    except Exception as e:
        logger.error(f"召回字段取值失败：{e}")
        writer({"type": "progress", "step": "召回字段取值", "status": "error"})
        raise
