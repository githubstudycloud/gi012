# 智谱 API 接入 Codex CLI、Claude Code、Gemini CLI 研究

## 概述

本文档研究如何将智谱(Zhipu AI)的 GLM 系列模型 API 接入到 OpenAI Codex CLI、Claude Code 和 Google Gemini CLI。

**测试状态**: ✅ 三个工具全部验证可用 (2025-01-05)

## 研究总结

### 核心发现

1. **智谱提供两种 API 格式**：
   - Anthropic 兼容格式：专为 Claude Code 设计
   - OpenAI 兼容格式：适用于 Codex CLI 和 Gemini CLI

2. **接入难度排序**：Claude Code (最简单) > Codex CLI (简单) > Gemini CLI (中等)

3. **会话恢复支持**：
   - Claude Code: ✅ 支持 (`claude -c` 或 `claude -r`)
   - Codex CLI: ✅ 支持 (`codex resume --last`)
   - Gemini CLI: ❌ 不支持

### 测试环境

- **服务器**: Ubuntu 22.04.5 LTS
- **Node.js**: v20.18.0 (手动安装，无需 sudo)
- **测试日期**: 2026-01-05

### 测试结果

| 工具 | 版本 | 状态 | 响应示例 |
|------|------|------|----------|
| Claude Code | 2.0.76 | ✅ 正常 | "太好了！测试成功..." |
| Codex CLI | 0.77.0 | ✅ 正常 | "很高兴听到测试成功！..." |
| Gemini CLI | 定制版 | ✅ 正常 | "收到明白。" |

### 注意事项

- **Codex CLI**: 智谱仅支持 `wire_api = "chat"`，不支持 `responses`
- **Gemini CLI**: 需要修改源码中的模型映射逻辑，防止添加 `google/` 前缀
- **Telemetry 警告**: Gemini CLI 无法连接 Google 遥测服务器，不影响使用

## 快速开始

### 一键安装脚本

```bash
# 1. 下载安装脚本
wget https://raw.githubusercontent.com/githubstudycloud/gi012/main/zhipu-api-integration-research/install-ai-cli.sh

# 2. 编辑脚本，设置你的 API Key
nano install-ai-cli.sh  # 修改 ZHIPU_API_KEY="YOUR_API_KEY"

# 3. 执行安装
chmod +x install-ai-cli.sh
./install-ai-cli.sh

# 4. 加载环境变量
source ~/.bashrc
```

### 详细安装文档

- **[完整操作记录（新手推荐）](docs/step-by-step-setup.md)** - 逐步命令，可直接复制执行
- [Claude Code 安装配置指南](docs/claude-code-setup.md)
- [Codex CLI 安装配置指南](docs/codex-cli-setup.md)
- [Gemini CLI 安装配置指南](docs/gemini-cli-setup.md)
- [Docker 安装与 GitLab 自建探究](docs/docker-gitlab-exploration.md)

---

## 智谱 API 官方端点

根据[官方文档](https://docs.bigmodel.cn/cn/coding-plan/tool/others)：

| 用途 | Base URL |
|------|----------|
| Coding 专用 (OpenAI格式) | `https://open.bigmodel.cn/api/coding/paas/v4` |
| Claude Code (Anthropic格式) | `https://open.bigmodel.cn/api/anthropic` |

### 可用模型

- **GLM-4.7**: 最新旗舰模型，358B MoE 架构
- **GLM-4.6**: 355B MoE 架构，200K 上下文
- **GLM-4.5-air**: 轻量版本

---

## Claude Code 接入方案 ✅ 已验证

根据[官方文档](https://docs.bigmodel.cn/cn/coding-plan/tool/claude)：

### 方法 1: 使用官方助手（推荐）

```bash
npx @z_ai/coding-helper
```

### 方法 2: 手动配置

编辑 `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-zhipu-api-key",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

### 模型映射

| Claude 模型 | 智谱模型 |
|-------------|----------|
| Opus | GLM-4.7 |
| Sonnet | GLM-4.7 |
| Haiku | GLM-4.5-Air |

### 测试结果

```bash
$ echo "just reply: test ok" | claude -p
test ok
```

---

## Codex CLI 接入方案 ✅ 已验证

### 配置文件

`~/.codex/config.toml`:

```toml
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
```

### 环境变量

```bash
export ZHIPU_API_KEY="your-api-key"
```

### 使用方法

```bash
# 交互模式
codex -c model_provider=zhipu -c model=glm-4.7

# 非交互模式
echo "your prompt" | codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto
```

### 测试结果

```
$ echo "just say hello" | codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto
--------
model: glm-4.7
provider: zhipu
--------
Hello! How can I help you today?
```

---

## Gemini CLI 接入方案 ✅ 已验证

根据[官方文档](https://docs.bigmodel.cn/cn/guide/develop/gemini)，需要使用**定制版 Gemini CLI**。

### 安装步骤

```bash
# 1. 克隆定制版仓库
git clone https://github.com/heartyguy/gemini-cli
cd gemini-cli

# 2. 切换到兼容分支
git checkout feature/openrouter-support

# 3. 安装依赖并构建
npm install
npm run build

# 4. 设置环境变量
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="your-zhipu-api-key"
```

### 重要：修改模型映射

定制版默认会给模型名添加 `google/` 前缀，需要修改 `packages/core/src/core/contentGenerator.ts` 第 38 行:

```typescript
// 原代码
return modelMap[model] || `google/${model}`;

// 改为（支持 GLM 模型）
return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google/${model}`);
```

修改后重新构建: `npm run build`

### 使用方法

```bash
# 运行 (stderr 会有 telemetry 超时警告，可忽略)
echo "your prompt" | node packages/cli/dist/index.js -m glm-4.7 -p 2>/dev/null
```

### 测试结果

```bash
$ echo "say hi" | node packages/cli/dist/index.js -m glm-4.7 -p 2>/dev/null
Hi
```

---

## 工具对比

| 特性 | Claude Code | Codex CLI | Gemini CLI |
|------|-------------|-----------|------------|
| 智谱支持 | ✅ 原生 | ✅ 原生 | ✅ 定制版 |
| 配置方式 | settings.json | config.toml | 环境变量+源码修改 |
| API 格式 | Anthropic | OpenAI | OpenAI |
| 接入难度 | 简单 | 简单 | 中等 |

---

## 快速安装 (Ubuntu)

```bash
# 1. 安装 Node.js
wget https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz
tar -xf node-v20.18.0-linux-x64.tar.xz
mv node-v20.18.0-linux-x64 ~/nodejs
echo 'export PATH=$HOME/nodejs/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# 2. 安装 CLI 工具
npm install -g @anthropic-ai/claude-code @openai/codex

# 3. 配置环境变量
export ZHIPU_API_KEY="your-api-key"

# 4. 配置 Claude Code
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-api-key",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
EOF

# 5. 配置 Codex CLI
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
EOF

# 6. 测试
claude --version
codex --version
```

---

## 参考资料

- [智谱 Coding Plan 官方文档](https://docs.bigmodel.cn/cn/coding-plan/tool/others)
- [智谱 Claude Code 接入文档](https://docs.bigmodel.cn/cn/coding-plan/tool/claude)
- [智谱 Gemini CLI 接入文档](https://docs.bigmodel.cn/cn/guide/develop/gemini)
- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [Codex CLI 配置参考](https://developers.openai.com/codex/config-reference/)
- [Gemini CLI 定制版 GitHub](https://github.com/heartyguy/gemini-cli)
