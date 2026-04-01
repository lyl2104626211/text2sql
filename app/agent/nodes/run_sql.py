from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from app.core.log import logger


async def run_sql(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "运行SQL", "status": "running"})
    try:
        sql = state["sql"]
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        res = await dw_mysql_repository.run_sql(sql)
        logger.info(f"SQL运行结果：{res}")
        writer({"type": "progress", "step": "运行SQL", "status": "success"})
        writer({"type": "result", "data": res})
        return {"sql_result": res}
    except Exception as e:
        logger.error(f"运行SQL失败：{e}")
        writer({"type": "progress", "step": "运行SQL", "status": "error"})
        raise
