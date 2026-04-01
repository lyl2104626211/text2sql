# Agent Data - Text-to-SQL 智能查询 Agent

## 项目简介

Agent Data 是一个基于大语言模型（LLM）的 Text-to-SQL 智能查询系统。用户可以用自然语言提出数据查询需求，系统自动完成关键词提取、字段召回、SQL 生成与执行，返回查询结果。

## 技术架构

### 核心技术栈

- **Web 框架**: FastAPI
- **Agent 编排**: LangGraph
- **向量数据库**: Qdrant（用于字段、指标召回）
- **全文检索引擎**: Elasticsearch（用于字段值召回）
- **关系型数据库**: MySQL（元数据库 + 数据仓库）
- **嵌入模型**: BGE-large-zh-v1.5（HuggingFace）

### Agent 处理流程

系统采用 LangGraph 状态图编排，包含以下节点：

```
用户查询
    ↓
extract_keywords（关键词提取）
    ↓
├── recall_column（召回字段）
├── recall_value（召回字段取值）
└── recall_metric（召回指标）
    ↓
merge_retrieved_info（合并召回信息）
    ↓
├── filter_table（筛选表）
└── filter_metric（筛选指标）
    ↓
add_extra_context（补充上下文）
    ↓
generate_sql（生成 SQL）
    ↓
validate_sql（校验 SQL）
    ↓
├── run_sql（执行 SQL）  ← 通过校验
└── correct_sql（修正 SQL）← 校验失败
    ↓
返回结果
```

## 项目结构

```
agent_data/
├── app/
│   ├── agent/               # Agent 核心模块
│   │   ├── nodes/           # LangGraph 节点实现
│   │   │   ├── extract_keywords.py    # 关键词提取
│   │   │   ├── recall_column.py        # 召回字段
│   │   │   ├── recall_value.py         # 召回字段取值
│   │   │   ├── recall_metric.py        # 召回指标
│   │   │   ├── merge_retrieved_info.py # 合并召回信息
│   │   │   ├── filter_table.py         # 筛选表
│   │   │   ├── filter_metric.py        # 筛选指标
│   │   │   ├── add_extra_context.py    # 补充上下文
│   │   │   ├── generate_sql.py         # 生成 SQL
│   │   │   ├── validate_sql.py         # 校验 SQL
│   │   │   ├── correct_sql.py          # 修正 SQL
│   │   │   └── run_sql.py              # 执行 SQL
│   │   ├── context.py       # Agent 上下文
│   │   ├── state.py         # Agent 状态定义
│   │   ├── graph.py         # LangGraph 流程图定义
│   │   └── llm.py           # LLM 配置
│   ├── api/                 # API 层
│   │   ├── routers/         # 路由定义
│   │   ├── schemas/        # Pydantic 数据模型
│   │   ├── dependencies.py # 依赖注入
│   │   └── lifespan.py     # 生命周期管理
│   ├── client/              # 各服务客户端管理
│   │   ├── mysql_client_manager.py     # MySQL 客户端
│   │   ├── es_client_manager.py        # ES 客户端
│   │   ├── qdrant_client_manager.py    # Qdrant 客户端
│   │   └── emdding_client_manager.py   # Embedding 客户端
│   ├── repositories/        # 数据访问层
│   │   ├── mysql/           # MySQL 仓储
│   │   ├── qdrant/          # Qdrant 向量检索
│   │   └── es/              # Elasticsearch 检索
│   ├── services/            # 业务服务层
│   ├── pojo/                # 数据对象
│   ├── service_pojo/        # 服务层数据对象
│   ├── prompt/              # Prompt 模板加载器
│   ├── config/              # 配置管理
│   └── core/                # 核心工具
├── config/
│   ├── app_config.yaml      # 应用配置
│   └── meta_config.yaml      # 元数据配置（表、字段、指标定义）
├── docker/
│   ├── docker-compose.yaml   # 基础设施编排
│   ├── mysql/                # MySQL 初始化脚本
│   └── elasticsearch/        # ES 配置文件
├── prompts/                  # Prompt 模板文件
├── main.py                   # 应用入口
└── pyproject.toml            # 项目依赖
```

## 快速开始

### 环境要求

- Python 3.11+
- Docker & Docker Compose
- NVIDIA GPU（用于 Embedding 模型加速，推荐）

### 1. 启动基础设施

```bash
cd docker
docker-compose up -d
```

这将启动：
- MySQL（端口 3306）
- Elasticsearch（端口 9200）
- Qdrant（端口 6333）
- Embedding 服务（端口 8081）

### 2. 安装依赖

```bash
pip install -r pyproject.toml
# 或使用 uv
uv sync
```

### 3. 配置数据库

编辑 `config/app_config.yaml`，修改 MySQL 连接信息：

```yaml
db_meta:
  host: localhost
  port: 3306
  user: your_user
  password: your_password
  database: meta

db_dw:
  host: localhost
  port: 3306
  user: your_user
  password: your_password
  database: dw
```

### 4. 构建元数据知识库

首次使用需要将元数据（表、字段、指标）同步到向量数据库：

```bash
python -m app.scripts.build_meta_knowledge
```

### 5. 启动服务

```bash
uvicorn main:app --reload
```

服务启动后访问 http://localhost:8000/docs 查看 API 文档。

## API 使用

### 查询接口

**端点**: `POST /api/query`

**请求体**:
```json
{
  "query": "统计华北地区2025年第一季度的销售总额"
}
```

**响应**: Server-Sent Events（SSE）流式返回

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "统计华北地区的销售总额"}'
```

## 配置说明

### 元数据配置 (meta_config.yaml)

定义数据仓库的表、字段、指标信息：

- `tables`: 表定义，包含表名、角色（dim/fact）、描述、字段列表
- `columns`: 字段定义，包含字段名、角色（dimension/measure/primary_key/foreign_key）、描述、别名
- `metrics`: 指标定义，包含指标名、描述、相关字段、别名

### 应用配置 (app_config.yaml)

| 配置项 | 说明 |
|--------|------|
| logging | 日志配置 |
| db_meta | 元数据库连接 |
| db_dw | 数据仓库连接 |
| qdrant | Qdrant 向量数据库连接 |
| embedding | Embedding 服务配置 |
| es | Elasticsearch 连接 |
| llm | 大语言模型配置 |

## 开发指南

### 添加新的 Agent 节点

1. 在 `app/agent/nodes/` 下创建节点文件
2. 实现节点函数，接收 `state` 和 `runtime` 参数
3. 在 `app/agent/graph.py` 中注册节点并定义边关系

### 修改 Prompt 模板

Prompt 模板位于 `prompts/` 目录，修改后重启服务即可生效。

## 许可证

MIT License
