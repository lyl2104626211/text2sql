from langchain.chat_models import init_chat_model
from app.config.app_config import app_config

llm = init_chat_model(
    model=app_config.llm.model_name,
    temperature=0,
    model_provider="openai",
    api_key=app_config.llm.api_key,
    base_url=app_config.llm.base_url,
    extra_body={"reasoning_split": True}  # 关键参数
)
