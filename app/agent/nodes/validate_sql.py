from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from app.core.log import logger


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "验证SQL", "status": "running"})
    try:
        sql = state["sql"]
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        try:
            await dw_mysql_repository.validate_sql(sql)
            logger.info(f"SQL正确")
            writer({"type": "progress", "step": "验证SQL", "status": "success"})
            return {"error": None}
        except Exception as e:
            logger.error(f"sql错误：{e}")
            writer({"type": "progress", "step": "验证SQL", "status": "success"})
            return {"error": str(e)}
    except Exception as e:
        logger.error(f"验证SQL失败：{e}")
        writer({"type": "progress", "step": "验证SQL", "status": "error"})
        raise
