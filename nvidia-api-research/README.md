# NVIDIA NIM API 研究报告

## 概述

NVIDIA NIM (NVIDIA Inference Microservices) 是 NVIDIA 提供的 AI 模型推理服务平台，提供了大量免费的 AI 模型用于原型开发和测试。

- **官方网站**: https://build.nvidia.com/
- **API 端点**: `https://integrate.api.nvidia.com/v1/`
- **API 兼容性**: OpenAI API 格式兼容

## 免费额度

根据 NVIDIA Developer Program:

| 项目 | 额度 |
|------|------|
| 开发者计划 | 免费访问 API 端点用于原型开发 |
| 自托管 NIM | 最多 16 个 GPU 用于研究和开发 |
| 企业评估 | 90 天免费评估许可证 |

> **注意**: 生产环境需要 NVIDIA AI Enterprise 许可证（$4,500/GPU/年 或 ~$1/GPU/小时）

## 可用模型列表

### 1. LLM 对话模型 (已测试通过)

| 模型 ID | 提供商 | 描述 |
|---------|--------|------|
| `meta/llama-3.3-70b-instruct` | Meta | Llama 3.3 70B 指令模型 |
| `meta/llama-3.1-405b-instruct` | Meta | Llama 3.1 405B 超大模型 |
| `meta/llama-3.1-70b-instruct` | Meta | Llama 3.1 70B 指令模型 |
| `meta/llama-3.1-8b-instruct` | Meta | Llama 3.1 8B 轻量模型 |
| `deepseek-ai/deepseek-r1` | DeepSeek | DeepSeek R1 推理模型 |
| `deepseek-ai/deepseek-v3.1` | DeepSeek | DeepSeek V3.1 模型 |
| `deepseek-ai/deepseek-v3.2` | DeepSeek | DeepSeek V3.2 最新版 |
| `qwen/qwq-32b` | Qwen | 通义千问 QwQ 推理模型 |
| `qwen/qwen3-235b-a22b` | Qwen | 通义千问 3 超大模型 |
| `google/gemma-3-27b-it` | Google | Gemma 3 27B 指令模型 |
| `microsoft/phi-4-mini-instruct` | Microsoft | Phi-4 Mini 指令模型 |
| `mistralai/mistral-large-3-675b-instruct-2512` | Mistral | Mistral Large 3 675B |
| `mistralai/mistral-small-3.1-24b-instruct-2503` | Mistral | Mistral Small 3.1 24B |

### 2. NVIDIA 自研模型

| 模型 ID | 描述 |
|---------|------|
| `nvidia/nemotron-3-nano-30b-a3b` | Nemotron 3 Nano 30B |
| `nvidia/nemotron-4-340b-instruct` | Nemotron 4 340B 指令 |
| `nvidia/llama-3.1-nemotron-ultra-253b-v1` | Nemotron Ultra 253B |
| `nvidia/llama-3.3-nemotron-super-49b-v1.5` | Nemotron Super 49B |
| `nvidia/cosmos-reason2-8b` | Cosmos Reason 物理 AI |

### 3. 代码模型

| 模型 ID | 提供商 | 描述 |
|---------|--------|------|
| `qwen/qwen2.5-coder-32b-instruct` | Qwen | 通义千问 Coder 32B |
| `qwen/qwen3-coder-480b-a35b-instruct` | Qwen | 通义千问 Coder 480B |
| `mistralai/codestral-22b-instruct-v0.1` | Mistral | Codestral 22B |
| `mistralai/devstral-2-123b-instruct-2512` | Mistral | Devstral 123B |
| `bigcode/starcoder2-15b` | BigCode | StarCoder2 15B |
| `deepseek-ai/deepseek-coder-6.7b-instruct` | DeepSeek | DeepSeek Coder |

### 4. 嵌入模型 (已测试通过)

| 模型 ID | 描述 |
|---------|------|
| `nvidia/nv-embedqa-e5-v5` | NVIDIA 问答嵌入模型 |
| `nvidia/nv-embed-v1` | NVIDIA 通用嵌入模型 |
| `nvidia/llama-3.2-nv-embedqa-1b-v2` | Llama 嵌入模型 |
| `baai/bge-m3` | BGE-M3 多语言嵌入 |
| `snowflake/arctic-embed-l` | Arctic 嵌入模型 |

### 5. 视觉语言模型

| 模型 ID | 描述 |
|---------|------|
| `meta/llama-3.2-90b-vision-instruct` | Llama 3.2 90B 视觉 |
| `meta/llama-3.2-11b-vision-instruct` | Llama 3.2 11B 视觉 |
| `nvidia/nemotron-nano-12b-v2-vl` | Nemotron 视觉语言 |
| `microsoft/phi-4-multimodal-instruct` | Phi-4 多模态 |
| `microsoft/phi-3.5-vision-instruct` | Phi-3.5 视觉 |

### 6. 推理模型 (Reasoning)

| 模型 ID | 描述 |
|---------|------|
| `deepseek-ai/deepseek-r1` | DeepSeek R1 推理 |
| `deepseek-ai/deepseek-r1-0528` | DeepSeek R1 0528版 |
| `qwen/qwq-32b` | QwQ 32B 推理模型 |
| `qwen/qwen3-next-80b-a3b-thinking` | Qwen3 思考模型 |
| `moonshotai/kimi-k2-thinking` | Kimi K2 思考模型 |
| `microsoft/phi-4-mini-flash-reasoning` | Phi-4 推理模型 |

## API 使用示例

### 对话补全

```bash
curl https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -d '{
    "model": "meta/llama-3.3-70b-instruct",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### 嵌入生成

```bash
curl https://integrate.api.nvidia.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -d '{
    "model": "nvidia/nv-embedqa-e5-v5",
    "input": ["Your text here"],
    "input_type": "query"
  }'
```

### Python 示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="your-nvidia-api-key"
)

response = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100
)

print(response.choices[0].message.content)
```

## 测试结果

### 成功测试的模型

| 模型 | 状态 | 响应时间 | 备注 |
|------|------|----------|------|
| meta/llama-3.3-70b-instruct | 正常 | ~2s | 响应质量高 |
| deepseek-ai/deepseek-r1 | 正常 | ~5s | 带推理过程 |
| qwen/qwq-32b | 正常 | ~3s | 中文支持好 |
| microsoft/phi-4-mini-instruct | 正常 | ~1s | 响应快速 |
| google/gemma-3-27b-it | 正常 | ~2s | 质量稳定 |
| mistralai/mistral-large-3-675b | 正常 | ~3s | 最大模型之一 |
| nvidia/nv-embedqa-e5-v5 | 正常 | ~1s | 嵌入维度 1024 |

### 返回 404 的模型

部分模型可能需要特殊权限或仅限特定账户:
- `nvidia/llama-3.1-nemotron-70b-instruct`

## 注意事项

1. **API Key 格式**: 以 `nvapi-` 开头
2. **请求限制**: 免费账户有速率限制，具体数值未公开
3. **Token 计费**: 基于 prompt_tokens + completion_tokens
4. **模型可用性**: 部分模型可能临时不可用
5. **数据隐私**: 请勿发送敏感数据

## 相关链接

- [NVIDIA NIM](https://developer.nvidia.com/nim)
- [API 目录](https://build.nvidia.com/)
- [文档](https://docs.api.nvidia.com/nim/docs/product)
- [开发者论坛](https://forums.developer.nvidia.com/)

---

*文档生成时间: 2025-01*
