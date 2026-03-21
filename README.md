# 📚 Smart Learning Assistant

一个基于 **多智能体（Multi-Agent）架构** 的智能学习助手。用户上传课程资料后，系统可自动提供**出题、笔记整理、知识问答**等服务，并通过本地 RAG + 联网搜索的方式，智能回答用户问题。

## ✨ 核心功能

-   **📄 课程与资料管理**：支持创建/删除课程，上传/管理 PDF、TXT 等格式的学习资料。
-   **🤖 多智能体协同**：利用 `LangGraph` 编排路由、检索、生成等多个 Agent，精准识别用户意图并执行任务。
-   **🔍 混合检索策略**：优先基于 `Chroma` 向量库进行语义检索，当本地知识不足时，自动触发联网搜索，融合两者信息生成答案。
-   **💾 智能缓存**：使用 `Redis` 实现语义缓存，对高频、相似问题快速响应，提升效率。
-   **🎨 Web 交互界面**：基于 `FastAPI` + 原生 HTML/CSS/JS 构建，支持课程切换、文件预览下载、聊天对话等操作。

## 🛠️ 技术栈

-   **Agent 框架**：`LangGraph`, `LangChain`
-   **后端框架**：`FastAPI`
-   **向量数据库**：`Chroma`
-   **缓存**：`Redis`
-   **前端**：HTML5, CSS3, JavaScript
-   **部署**：`Docker`

## 🚀 快速开始

### 环境要求
-   Python 3.10+
-   Redis (用于缓存)

### 安装与运行

1.  **克隆仓库**
    ```bash
    git clone https://github.com/Cxz135/smart-learning-assistant.git
    cd smart-learning-assistant