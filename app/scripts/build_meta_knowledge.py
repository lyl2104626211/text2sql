import argparse
import asyncio
from pathlib import Path
from app.services.meta_knowledge_service import MetaKnowledgeService
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.client.mysql_client_manager import db_meta_manager, db_dw_manager
from app.client.qdrant_client_manager import qdrant_manager
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.client.emdding_client_manager import embedding_manager
from app.client.es_client_manager import es_manager
from app.repositories.es.value_repository import ValueESRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

async def build_meta_knowledge(config: Path):
    embedding_manager.init()
    db_meta_manager.init()
    db_dw_manager.init()
    qdrant_manager.init()
    es_manager.init()
    embedding_model = embedding_manager.client
    async with db_meta_manager.session_factory() as db_meta_session, db_dw_manager.session_factory() as db_dw_session:
        meta_repository = MetaMysqlRepository(db_meta_session)
        dw_mysql_repository = DwMysqlRepository(db_dw_session)
        value_es_repository = ValueESRepository(es_manager.client)
        metric_qdrant_repository = MetricQdrantRepository(qdrant_manager.client)
        column_qdrant_repository = ColumnQdrantRepository(qdrant_manager.client)
        knowledge_service = MetaKnowledgeService(meta_mysql_repository=meta_repository,
                                                 dw_mysql_repository=dw_mysql_repository,
                                                 column_qdrant_repository=column_qdrant_repository,
                                                 embedding_model=embedding_model,
                                                 value_es_repository=value_es_repository,
                                                 metric_qdrant_repository=metric_qdrant_repository)

        await knowledge_service.build(config)
    await db_meta_manager.close()
    await db_dw_manager.close()
    await qdrant_manager.close()
    await es_manager.close()

if __name__ == '__main__':
    paser = argparse.ArgumentParser()
    paser.add_argument('data_path')
    args = paser.parse_args()
    asyncio.run(build_meta_knowledge(Path(args.data_path)))
