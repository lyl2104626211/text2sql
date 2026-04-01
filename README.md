# Data Agent Frontend

数据代理前端应用，基于 Vue 3 + Vite 构建，提供自然语言查询界面。

## 功能特性

- **自然语言查询**：用户可以通过输入自然语言问题查询数据
- **实时进度展示**：以步骤气泡的形式实时展示查询进度（运行中/成功/错误）
- **表格结果展示**：以表格形式展示查询结果
- **流式响应**：通过 Server-Sent Events（SSE）接收后端流式数据
- **悬浮输入框**：固定在底部的现代化悬浮输入框设计

## 项目结构

```
data-agent-fronted/
├── public/                  # 静态资源
│   └── vite.svg            # Vite 图标
├── src/
│   ├── assets/             # 项目资源
│   │   └── vue.svg         # Vue 图标
│   ├── components/         # Vue 组件（预留）
│   │   └── HelloWorld.vue
│   ├── App.vue             # 主应用组件（聊天界面）
│   ├── main.js             # 应用入口
│   └── style.css           # 全局样式
├── index.html              # HTML 入口
├── package.json            # 项目配置
└── vite.config.js         # Vite 配置（含 API 代理）
```

## 技术栈

- **前端框架**：Vue 3（`<script setup>` 语法）
- **构建工具**：Vite 7.x
- **Vue 插件**：@vitejs/plugin-vue 6.x

## 安装与运行

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

启动后访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## API 配置

前端通过 `/api/query` 路径向后端发送查询请求。开发环境下，Vite 会将请求代理到 `http://localhost:8000`。

### 请求格式

```json
POST /api/query
Content-Type: application/json

{
  "query": "你的问题"
}
```

### 响应格式（Server-Sent Events）

后端返回多种类型的数据：

**进度更新**
```
data: {"type": "progress", "step": "理解问题", "status": "running"}
data: {"type": "progress", "step": "理解问题", "status": "success"}
```

**表格结果**
```
data: {"type": "result", "data": [{"列名": "值", ...}, ...]}
```

**错误信息**
```
data: {"type": "error", "message": "错误描述"}
```

## 界面说明

- **左侧头像（🤖）**：助手消息
- **右侧头像（🧑）**：用户消息
- **进度气泡**：黄色=运行中，绿色=成功，红色=错误
- **表格**：自动横向滚动，列名固定在顶部

## 注意事项

- 请确保后端服务运行在 http://localhost:8000
- 样式已在 `App.vue` 中覆盖了 Vite 默认样式
