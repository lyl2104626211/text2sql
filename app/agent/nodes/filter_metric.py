import yaml

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, MetricInfoState
from langgraph.runtime import Runtime
from app.core.log import logger
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt


async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤指标信息", "status": "running"})
    try:
        # a=1/0
        query = state["query"]
        metric_infos = state["metric_infos"]
        before_metric_name = [metric_info["name"] for metric_info in metric_infos]
        logger.info(f"原始指标信息：{before_metric_name}")
        # 调用 LLM 根据用户 query 筛选相关表及其列
        prompt_template = PromptTemplate(template=load_prompt("filter_metric_info"),
                                         input_variables=["query", "metric_infos"])
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        res = await chain.ainvoke({"query": query,
                                   "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False)})
        # 解析 LLM 返回结果：根据返回的表名和列名过滤 metric_infos
        filter_metric_info: list[MetricInfoState] = []
        if res:
            for metric_info in metric_infos:
                if metric_info["name"] in res:
                    filter_metric_info.append(metric_info)
            metric_info = [metric_info["name"] for metric_info in filter_metric_info]
            logger.info(f"过滤后的指标信息：{metric_info}")
        writer({"type": "progress", "step": "过滤指标信息", "status": "success"})
        return {"metric_infos": filter_metric_info}
    except Exception as e:
        logger.error(f"过滤指标信息失败：{e}")
        writer({"type": "progress", "step": "过滤指标信息", "status": "error"})
        raise
