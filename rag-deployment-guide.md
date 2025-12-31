# RAG 三种方案部署实战指南

本文详细介绍 GraphRAG、LightRAG、Hybrid RAG 的具体实现和部署方法。

---

## 一、Hybrid RAG（推荐入门）

**原理**：向量检索 + BM25 关键词检索，结果融合排序

### 1.1 环境准备

```bash
conda create -n hybrid-rag python=3.12
conda activate hybrid-rag
pip install langchain openai faiss-cpu rank-bm25 sentence-transformers chromadb
```

### 1.2 核心代码实现

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

# 1. 准备文档
documents = [
    Document(page_content="GraphRAG 使用知识图谱增强检索"),
    Document(page_content="LightRAG 是轻量级的图增强 RAG"),
    Document(page_content="Hybrid RAG 结合向量和关键词搜索"),
    # ... 更多文档
]

# 2. 创建 BM25 检索器（关键词匹配）
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5  # 返回 top 5

# 3. 创建向量检索器（语义匹配）
vectorstore = Chroma.from_documents(documents, OpenAIEmbeddings())
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 4. 融合检索器（权重可调）
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6]  # BM25 占 40%，向量占 60%
)

# 5. 检索
results = ensemble_retriever.invoke("什么是轻量级 RAG？")
```

### 1.3 数据收集与输出

```python
import os
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PDFLoader,
    UnstructuredMarkdownLoader
)

# 收集数据：支持多种格式
loader = DirectoryLoader(
    "./data",
    glob="**/*.txt",  # 可改为 *.pdf, *.md 等
    loader_cls=TextLoader
)
documents = loader.load()

# 文本分块
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# 输出成果：问答
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

llm = ChatOpenAI(model="gpt-4o-mini")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=ensemble_retriever,
    return_source_documents=True
)

result = qa_chain.invoke({"query": "你的问题"})
print(result["result"])  # 答案
print(result["source_documents"])  # 来源文档
```

### 1.4 成本估算

| 项目 | 成本 |
|------|------|
| Embedding | ~$0.0001/1K tokens (text-embedding-3-small) |
| LLM 问答 | ~$0.15/1M tokens (gpt-4o-mini) |
| **总计** | 10万文档约 $5-20 |

---

## 二、LightRAG（性价比之选）

**原理**：轻量级知识图谱 + 向量检索，平衡效果与成本

### 2.1 安装

```bash
# 方式一：pip 安装
pip install "lightrag-hku[api]"

# 方式二：源码安装
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
pip install -e ".[api]"

# 方式三：Docker
docker compose up
```

### 2.2 基础使用

```python
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

async def main():
    # 初始化
    rag = LightRAG(
        working_dir="./lightrag_storage",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    await rag.initialize_storages()

    # 插入数据
    with open("your_document.txt", "r", encoding="utf-8") as f:
        await rag.ainsert(f.read())

    # 查询（6种模式可选）
    result = await rag.aquery(
        "你的问题",
        param=QueryParam(mode="hybrid")  # 推荐 hybrid 模式
    )
    print(result)

asyncio.run(main())
```

### 2.3 查询模式对比

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `naive` | 纯向量检索 | 简单问答 |
| `local` | 局部图检索 | 特定实体查询 |
| `global` | 全局图检索 | 宏观总结 |
| `hybrid` | local + global | **通用推荐** |
| `mix` | 图 + 向量 | 复杂问题 |
| `bypass` | 直接问 LLM | 不需要检索时 |

### 2.4 支持的存储后端

```python
# 向量存储：Chroma / Milvus / Qdrant / FAISS / PostgreSQL
from lightrag.kg.chroma_impl import ChromaVectorDBStorge

# 图存储：Neo4j / PostgreSQL / NetworkX
from lightrag.kg.neo4j_impl import Neo4JStorage

rag = LightRAG(
    working_dir="./storage",
    vector_storage=ChromaVectorDBStorge,
    graph_storage=Neo4JStorage,
    # ... 其他配置
)
```

### 2.5 API 服务部署

```bash
# 启动 API 服务
lightrag-server --port 8000

# 访问 Web UI
# http://localhost:8000
```

API 调用示例：
```bash
# 插入文档
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"text": "你的文档内容"}'

# 查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "你的问题", "mode": "hybrid"}'
```

### 2.6 成本估算

| 项目 | 成本 |
|------|------|
| 索引（图构建） | 比 GraphRAG 少 50-70% |
| Embedding | 与 Hybrid RAG 相同 |
| LLM 问答 | 与 Hybrid RAG 相同 |
| **总计** | 10万文档约 $20-50 |

---

## 三、GraphRAG（重型武器）

**原理**：完整知识图谱构建，实体提取 + 关系抽取 + 社区检测

### 3.1 安装

```bash
pip install graphrag

# 或使用 Azure 加速器（一键部署）
git clone https://github.com/Azure-Samples/graphrag-accelerator.git
```

### 3.2 初始化项目

```bash
mkdir my_graphrag && cd my_graphrag
graphrag init --root .
```

生成的目录结构：
```
my_graphrag/
├── .env              # API 密钥配置
├── settings.yaml     # 详细配置
└── input/            # 放入你的文档（.txt 或 .csv）
```

### 3.3 配置 .env

```env
GRAPHRAG_API_KEY=your-openai-api-key
```

### 3.4 配置 settings.yaml（关键配置）

```yaml
llm:
  model: gpt-4o-mini  # 推荐用便宜模型做索引
  api_base: https://api.openai.com/v1

embeddings:
  model: text-embedding-3-small

chunks:
  size: 1200
  overlap: 100

entity_extraction:
  max_gleanings: 1  # 减少这个值可降低成本

community_reports:
  max_length: 2000
```

### 3.5 收集数据

```bash
# 将文档放入 input 目录（支持 .txt 和 .csv）
cp your_documents/*.txt ./input/

# 或者用脚本批量转换
python -c "
import os
from pathlib import Path

# 将 PDF 转为 txt（需要 pymupdf）
import fitz

for pdf_file in Path('./pdfs').glob('*.pdf'):
    doc = fitz.open(pdf_file)
    text = ''.join([page.get_text() for page in doc])
    output = Path('./input') / f'{pdf_file.stem}.txt'
    output.write_text(text, encoding='utf-8')
"
```

### 3.6 构建索引

```bash
# 构建知识图谱（耗时耗钱的步骤！）
graphrag index --root .

# 查看进度
tail -f output/indexing-logs/*.log
```

### 3.7 查询

```bash
# 全局查询（跨文档总结）
graphrag query --root . --method global --query "所有文档的共同主题是什么？"

# 局部查询（具体问题）
graphrag query --root . --method local --query "某个具体问题"
```

Python 调用：
```python
import asyncio
from graphrag.query.cli import run_global_search, run_local_search

# 全局搜索
result = asyncio.run(run_global_search(
    root_dir=".",
    query="跨文档的宏观总结问题"
))
print(result)
```

### 3.8 输出成果

索引完成后，`output/` 目录包含：
```
output/
├── artifacts/
│   ├── entities.parquet      # 提取的实体
│   ├── relationships.parquet # 实体关系
│   ├── communities.parquet   # 社区聚类
│   └── community_reports.parquet  # 社区报告
└── indexing-logs/
```

可视化知识图谱：
```python
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 读取实体和关系
entities = pd.read_parquet("output/artifacts/entities.parquet")
relationships = pd.read_parquet("output/artifacts/relationships.parquet")

# 构建图
G = nx.from_pandas_edgelist(
    relationships,
    source='source',
    target='target',
    edge_attr='description'
)

# 绘制
plt.figure(figsize=(20, 20))
nx.draw(G, with_labels=True, node_size=100, font_size=8)
plt.savefig("knowledge_graph.png", dpi=300)
```

### 3.9 成本估算（重要！）

| 项目 | 成本 |
|------|------|
| 实体提取 | ~$2-5 / 1MB 文本 |
| 关系抽取 | ~$1-3 / 1MB 文本 |
| 社区报告 | ~$0.5-1 / 1MB 文本 |
| **总计** | 10万文档约 $200-500+ |

---

## 四、方案对比总结

| 维度 | Hybrid RAG | LightRAG | GraphRAG |
|------|------------|----------|----------|
| **安装难度** | 简单 | 中等 | 复杂 |
| **索引成本** | 低（$5-20） | 中（$20-50） | 高（$200-500+） |
| **索引速度** | 快（分钟级） | 中（小时级） | 慢（天级） |
| **跨文档能力** | 弱 | 中 | 强 |
| **维护成本** | 低 | 中 | 高 |
| **适用场景** | 90% 的问答需求 | 需要关联的问答 | 宏观分析总结 |

## 五、推荐路径

```
开始
  │
  ▼
你的需求是什么？
  │
  ├─► 简单问答、文档检索 ──► Hybrid RAG ✓
  │
  ├─► 需要一定的关联能力 ──► LightRAG ✓
  │
  └─► 必须跨文档宏观分析 ──► GraphRAG（准备好钱包）
```

---

## 参考资源

- [Microsoft GraphRAG GitHub](https://github.com/microsoft/graphrag)
- [GraphRAG 官方文档](https://microsoft.github.io/graphrag/get_started/)
- [LightRAG GitHub](https://github.com/HKUDS/LightRAG)
- [Hybrid Search 教程 - Machine Learning Plus](https://www.machinelearningplus.com/gen-ai/hybrid-search-vector-keyword-techniques-for-better-rag/)
- [LangChain Ensemble Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/ensemble)
