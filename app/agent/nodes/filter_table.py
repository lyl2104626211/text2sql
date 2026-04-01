from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, TableInfoState
from langgraph.runtime import Runtime
from app.agent.llm import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import yaml
from app.core.log import logger

from app.prompt.prompt_loader import load_prompt


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤表信息", "status": "running"})
    try:
        query = state["query"]
        table_infos = state["table_infos"]
        table_name = [table_info["name"] for table_info in table_infos]
        logger.info(f"原始表信息：{table_name}")
        # 调用 LLM 根据用户 query 筛选相关表及其列
        prompt_template = PromptTemplate(template=load_prompt("filter_table_info"),
                                         input_variables=["query", "table_infos"])
        output_parser = JsonOutputParser()

        chain = prompt_template | llm | output_parser
        res = await chain.ainvoke({"query": query,
                                   "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False)})
        # 解析 LLM 返回结果：根据返回的表名和列名过滤 table_infos
        filter_table_info: list[TableInfoState] = []
        for table_info in table_infos:
            if table_info["name"] in res:
                table_info["columns"] = [column_info for column_info in table_info["columns"]
                                         if column_info["name"] in res[table_info["name"]]]

                filter_table_info.append(table_info)

        filter_table_name = [table_info["name"] for table_info in filter_table_info]
        logger.info(f"过滤后的表信息：{filter_table_name}")
        writer({"type": "progress", "step": "过滤表信息", "status": "success"})
        return {"table_infos": filter_table_info}
    except Exception as e:
        logger.error(f"过滤表信息失败：{e}")
        writer({"type": "progress", "step": "过滤表信息", "status": "error"})
        raise
