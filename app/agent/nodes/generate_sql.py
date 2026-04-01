import yaml

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from app.agent.llm import llm
from langchain_core.prompts import PromptTemplate
from app.prompt.prompt_loader import load_prompt
from langchain_core.output_parsers import StrOutputParser
from app.core.log import logger


async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "生成SQL", "status": "running"})
    try:
        query = state["query"]
        table_infos = state["table_infos"]
        metric_infos = state["metric_infos"]
        date_info = state["date_info_state"]
        db_info = state["db_info_state"]
        prompt_template = PromptTemplate(template=load_prompt("generate_sql"),
                                         input_variables=["query", "metric_infos", "table_infos", "date_info", "db_info"])
        output_parser = StrOutputParser()
        chain = prompt_template | llm | output_parser
        sql = await chain.ainvoke({"query": query,
                                   "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
                                   "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
                                   "date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=False),
                                   "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False)
                                   })

        logger.info(f"生成的SQL：{sql}")
        writer({"type": "progress", "step": "生成SQL", "status": "success"})
        return {"sql": sql}
    except Exception as e:
        logger.error(f"生成SQL失败：{e}")
        writer({"type": "progress", "step": "生成SQL", "status": "error"})
        raise
