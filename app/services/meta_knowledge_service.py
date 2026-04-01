import uuid
from dataclasses import asdict
from pathlib import Path
from omegaconf import OmegaConf
from app.config.meta_config import MetaConfig
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.service_pojo import MetricServicePOJO, ColumnMetricServicePOJO
from app.service_pojo.table_service_pojo import TableServicePOJO
from app.service_pojo.column_service_pojo import ColumnServicePOJO
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from app.repositories.es.value_repository import ValueESRepository
from app.service_pojo.value_info_service_pojo import ValueInfo
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.core.log import logger


class MetaKnowledgeService:
    embedding_batch_size = 20

    def __init__(self, meta_mysql_repository: MetaMysqlRepository, dw_mysql_repository: DwMysqlRepository,
                 column_qdrant_repository: ColumnQdrantRepository, embedding_model: HuggingFaceEndpointEmbeddings,
                 value_es_repository: ValueESRepository, metric_qdrant_repository: MetricQdrantRepository):
        self.metric_qdrant_repository = metric_qdrant_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository
        self.column_qdrant_repository = column_qdrant_repository
        self.embedding_model = embedding_model
        self.value_es_repository = value_es_repository

    async def _save_tables_to_meta_db(self, meta_config: MetaConfig) -> list[ColumnServicePOJO]:
        # Step 1: 初始化存储结构
        table_infos: list[TableServicePOJO] = list()  # 存储所有表信息
        column_infos: list[ColumnServicePOJO] = list()  # 存储所有字段信息
        # Step 2: 遍历配置中的每个表定义
        for table in meta_config.tables:
            # 2.1 构建表信息对象
            #     从数据仓库查询该表的实际字段类型
            table_info = TableServicePOJO(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description
            )
            # 从数据仓库获取该表的字段类型字典 {字段名: 类型}
            column_types: dict = await self.dw_mysql_repository.get_columns(table.name)

            # 2.2 将表信息加入列表
            table_infos.append(table_info)

            # 2.3 遍历表中的每个字段，构建字段信息
            for column_info in table.columns:
                # 从数据仓库查询该字段的示例值（用于丰富元数据描述）
                values = await self.dw_mysql_repository.get_column_values(table.name, column_info.name)
                column_info = ColumnServicePOJO(
                    id=f"{table.name}.{column_info.name}",  # 唯一标识：表名.字段名
                    name=column_info.name,  # 字段名称
                    type=column_types[column_info.name],  # 字段类型（从数据仓库获取）
                    role=column_info.role,  # 字段角色（如主键、外键等）
                    description=column_info.description,  # 字段描述
                    alias=column_info.alias,  # 字段别名
                    examples=values,  # 字段示例值
                    table_id=table.name  # 所属表ID
                )
                column_infos.append(column_info)
        # 保存表和字段信息
        async with self.meta_mysql_repository.session.begin():
            self.meta_mysql_repository.save_tables(table_infos)
            self.meta_mysql_repository.save_columns(column_infos)
        return column_infos

    async def _save_columns_to_qdrant(self, column_infos: list[ColumnServicePOJO]):
        # 提取字段信息
        points: list[dict] = list()
        for column_info in column_infos:
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": column_info.name,
                "payload": asdict(column_info)
            })
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": column_info.description,
                "payload": asdict(column_info)
            })
            for alias in column_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": alias,
                    "payload": asdict(column_info)
                })
        # 获取向量点信息
        embedding_texts = [point["embedding_text"] for point in points]
        ids = [point["id"] for point in points]
        payloads = [point["payload"] for point in points]
        embeddings_values: list[list[float]] = list()
        # 获得点的文本向量化值
        for i in range(0, len(embedding_texts), self.embedding_batch_size):
            embedding_texts_batch = embedding_texts[i:i + self.embedding_batch_size]
            embeddings_values.extend(await self.embedding_model.aembed_documents(embedding_texts_batch))
        # Step 4: 建立向量索引
        await self.column_qdrant_repository.build_index()
        # Step 5: 将向量点存入向量数据库
        await self.column_qdrant_repository.upsert(ids, embeddings_values, payloads)

    async def _save_values_to_es(self, meta_config: MetaConfig):
        await self.value_es_repository.ensure_index()
        # 获取需要简历索引的字段
        value_infos: list[ValueInfo] = list()
        for table in meta_config.tables:
            for column in table.columns:
                if column.sync:
                    column_values = await self.dw_mysql_repository.get_column_values(table.name, column.name,
                                                                                     100000)
                    value_info = [ValueInfo(id=f"{table.name}.{column.name}.{column_value}", value=column_value,
                                            column_id=f"{table.name}.{column.name}") for column_value in
                                  column_values]

                    value_infos.extend(value_info)
        await self.value_es_repository.upsert(value_infos)

    async def _save_metrics_to_meta_db(self, meta_config: MetaConfig) -> list[MetricServicePOJO]:
        metric_infos: list[MetricServicePOJO] = list()
        metric_columns: list[ColumnMetricServicePOJO] = list()
        # 将指标信息存储meta_db
        for metric in meta_config.metrics:
            #  构建指标信息对象
            #     - id: 指标唯一标识，使用指标名称
            #     - name: 指标名称（如GMV、AOV）
            #     - description: 指标描述
            #     - relevant_columns: 关联字段列表（如fact_order.order_amount）
            #     - alias: 指标别名
            metric_info = MetricServicePOJO(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            )
            metric_infos.append(metric_info)
            for metric_column in metric.relevant_columns:
                metric_column_info = ColumnMetricServicePOJO(
                    column_id=metric_column,
                    metric_id=metric.name
                )
                metric_columns.append(metric_column_info)

        # 保存指标信息
        async with self.meta_mysql_repository.session.begin():
            self.meta_mysql_repository.save_metrics(metric_infos)
            self.meta_mysql_repository.save_column_metrics(metric_columns)
        return metric_infos

    async def _save_metric_info_to_qdrant(self, metric_infos: list[MetricServicePOJO]):
        points: list[dict] = list()
        for metric_column_info in metric_infos:
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": metric_column_info.name,
                "payload": asdict(metric_column_info)
            })
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": metric_column_info.description,
                "payload": asdict(metric_column_info)
            })
            for alias in metric_column_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": alias,
                    "payload": asdict(metric_column_info)
                })
        # 获取向量点信息
        embedding_texts = [point["embedding_text"] for point in points]
        ids = [point["id"] for point in points]
        payloads = [point["payload"] for point in points]
        embeddings_values: list[list[float]] = list()
        # 获得点的文本向量化值
        for i in range(0, len(embedding_texts), self.embedding_batch_size):
            embedding_texts_batch = embedding_texts[i:i + self.embedding_batch_size]
            embeddings_values.extend(await self.embedding_model.aembed_documents(embedding_texts_batch))
        # Step 4: 建立向量索引
        await self.metric_qdrant_repository.build_index()
        # Step 5: 将向量点存入向量数据库
        await self.metric_qdrant_repository.upsert(ids, embeddings_values, payloads)

    async def build(self, config: Path):
        """
        根据配置文件构建元数据知识库

        Args:
            config: OmegaConf配置文件路径，包含表、字段和指标的元数据定义
        """
        # Step 1: 加载并合并配置
        # - context: 从config文件加载原始配置
        # - schema: 基于MetaConfig生成结构化schema
        # - meta_config: 合并后的最终配置对象
        context = OmegaConf.load(config)
        schema = OmegaConf.structured(MetaConfig)
        logger.info("配置文件加载完成")
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        if meta_config.tables:
            # 将表信息和字段信息存入数据库
            column_infos = await self._save_tables_to_meta_db(meta_config)
            logger.info("将表信息和字段信息保存到数据库")
            # Step 2: 创建Qdrant向量索引,将字段信息写入向量数据库
            await self._save_columns_to_qdrant(column_infos)
            logger.info("为字段信息简历向量索引")
            # Step 3: 创建es 全文索引,将value构建全文索引
            await self._save_values_to_es(meta_config)
            logger.info("为字段的取值创建全文索引")

        if meta_config.metrics:
            # 将指标信息存入数据库
            metric_infos = await self._save_metrics_to_meta_db(meta_config)
            logger.info("将指标信息保存到数据库")
            # 将指标信息存入向量数据库
            await self._save_metric_info_to_qdrant(metric_infos)
            logger.info("为指标信息创建向量索引")
