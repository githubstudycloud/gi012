# Docker 容器化部署指南

本文档介绍如何使用 Docker 部署 Claude Code、Codex CLI 和 Gemini CLI，通过智谱 API 提供 AI 能力。

## 目录

- [前置条件](#前置条件)
- [快速开始](#快速开始)
- [各工具使用说明](#各工具使用说明)
- [单独构建镜像](#单独构建镜像)
- [常见问题](#常见问题)

## 前置条件

1. 安装 Docker 和 Docker Compose
2. 获取智谱 API Key：https://bigmodel.cn/usercenter/proj-mgmt/apikeys

## 快速开始

### 1. 配置 API Key

```bash
cd docker
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 2. 构建镜像

```bash
# 构建所有镜像
docker compose build

# 或单独构建某个镜像
docker compose build claude-code
docker compose build codex-cli
docker compose build gemini-cli  # 首次构建约需 5-10 分钟
```

### 3. 运行工具

```bash
# 运行 Claude Code
docker compose run --rm claude-code

# 运行 Codex CLI
docker compose run --rm codex-cli

# 运行 Gemini CLI
docker compose run --rm gemini-cli
```

## 各工具使用说明

### Claude Code

Claude Code 使用智谱 API 的 Anthropic 兼容接口。

```bash
# 交互模式
docker compose run --rm claude-code

# 管道模式
echo "你好" | docker compose run --rm claude-code -p

# 指定工作目录
docker compose run --rm -w /workspace/myproject claude-code
```

**环境变量说明**：
- `ANTHROPIC_AUTH_TOKEN`: 智谱 API Key
- `ANTHROPIC_BASE_URL`: https://open.bigmodel.cn/api/anthropic
- `API_TIMEOUT_MS`: 请求超时时间（默认 3000000ms）
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`: 禁用非必要流量

### Codex CLI

Codex CLI 使用智谱 API 的 OpenAI 兼容接口。

```bash
# 交互模式（自动配置 model_provider 和 model）
docker compose run --rm codex-cli

# 执行命令
docker compose run --rm codex-cli exec "分析当前目录的代码结构"

# 全自动模式
docker compose run --rm codex-cli exec --full-auto "创建一个简单的 Python 脚本"
```

**注意**：Codex CLI 需要在 Git 仓库中运行。容器内置的 entrypoint.sh 会在工作目录不存在 .git 时自动初始化。

**环境变量说明**：
- `ZHIPU_API_KEY`: 智谱 API Key（通过配置文件使用）

### Gemini CLI

Gemini CLI 使用定制版本，支持 OpenRouter 格式 API。

```bash
# 交互模式
docker compose run --rm gemini-cli

# 管道模式
echo "你好" | docker compose run --rm gemini-cli -p

# 指定模型
docker compose run --rm gemini-cli -m glm-4.7
```

**环境变量说明**：
- `OPENROUTER_BASE_URL`: https://open.bigmodel.cn/api/coding/paas/v4
- `OPENROUTER_API_KEY`: 智谱 API Key

## 单独构建镜像

如果不使用 docker-compose，可以单独构建和运行镜像。

### Claude Code

```bash
cd docker/claude-code
docker build -t claude-code-zhipu .

# 运行
docker run -it --rm \
  -e ANTHROPIC_AUTH_TOKEN=your-api-key \
  -e ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic \
  -e API_TIMEOUT_MS=3000000 \
  -e CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  -v $(pwd):/workspace \
  claude-code-zhipu
```

### Codex CLI

```bash
cd docker/codex-cli
docker build -t codex-cli-zhipu .

# 运行
docker run -it --rm \
  -e ZHIPU_API_KEY=your-api-key \
  -v $(pwd):/workspace \
  codex-cli-zhipu
```

### Gemini CLI

```bash
cd docker/gemini-cli
docker build -t gemini-cli-zhipu .  # 首次构建约需 5-10 分钟

# 运行
docker run -it --rm \
  -e OPENROUTER_API_KEY=your-api-key \
  -v $(pwd):/workspace \
  gemini-cli-zhipu
```

## 常见问题

### Q: Gemini CLI 构建很慢？

A: Gemini CLI 使用多阶段构建，需要从源码编译。首次构建约需 5-10 分钟，构建完成后重复运行会很快。

### Q: Codex CLI 报错 "not inside a git repository"？

A: Codex CLI 需要在 Git 仓库中运行。容器的 entrypoint.sh 会自动初始化，但如果挂载了已有目录且没有 .git，可以手动初始化：

```bash
docker compose run --rm codex-cli bash -c "git init && codex"
```

### Q: 如何持久化配置？

A: docker-compose.yml 已配置了命名卷用于持久化配置：
- `claude-code-config`: Claude Code 配置
- `codex-cli-config`: Codex CLI 配置

### Q: 如何使用自定义工作目录？

A: 修改 docker-compose.yml 中的 volumes 挂载：

```yaml
volumes:
  - /your/custom/path:/workspace
```

### Q: API 请求超时？

A: 智谱 API 响应可能较慢，已在配置中设置了较长的超时时间。如仍超时，可调整 `API_TIMEOUT_MS` 环境变量。

## 镜像大小参考

| 镜像 | 大小（约） |
|------|-----------|
| claude-code-zhipu | 300MB |
| codex-cli-zhipu | 350MB |
| gemini-cli-zhipu | 500MB |

## 相关文档

- [分步安装指南](./step-by-step-setup.md)
- [Claude Code 配置](./claude-code-setup.md)
- [Codex CLI 配置](./codex-cli-setup.md)
- [Gemini CLI 配置](./gemini-cli-setup.md)
