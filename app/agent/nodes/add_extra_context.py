from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from langgraph.runtime import Runtime
from datetime import datetime
from app.core.log import logger


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext] = None):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "添加额外上下文", "status": "running"})
    try:
        today = datetime.today()
        day_str = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month - 1) // 3 + 1}"
        date_info_state = DateInfoState(date=day_str, weekday=weekday, quarter=quarter)
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        db_info = await dw_mysql_repository.get_db_info()
        db_info_state = DBInfoState(**db_info)
        logger.info(f"日期信息：{date_info_state}")
        logger.info(f"数据库信息：{db_info_state}")
        writer({
            "type": "progress",
            "step": "添加额外上下文",
            "status": "success"
        })
        return {"date_info_state": date_info_state, "db_info_state": db_info_state}
    except Exception as e:
        logger.error(f"添加额外上下文失败：{e}")
        writer({"type": "progress", "step": "添加额外上下文", "status": "error"})
        raise
