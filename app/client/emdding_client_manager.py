from app.config.app_config import EmbeddingConfig, app_config
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: HuggingFaceEndpointEmbeddings | None = None

    def _geturl(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(model=self._geturl())


embedding_manager = EmbeddingClientManager(config=app_config.embedding)
if __name__ == '__main__':
    text = "What is deep learning?"
    query_result = embedding_manager.client.embed_query(text)
    print(query_result[:3])
