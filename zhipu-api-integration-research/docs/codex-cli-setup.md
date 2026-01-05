# Codex CLI 接入智谱 GLM 安装配置指南

## 概述

Codex CLI 是 OpenAI 官方的命令行编程助手。智谱提供了兼容 OpenAI API 格式的端点，可以通过配置自定义 Provider 使用 GLM 模型。

## 系统要求

- Node.js >= 18.x
- npm >= 8.x
- Git（用于 sandbox 功能）

## 安装步骤

### 1. 安装 Node.js（如未安装）

```bash
# Ubuntu/Debian - 方法1：使用包管理器
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 方法2：手动安装（无需 sudo）
wget https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz
tar -xf node-v20.18.0-linux-x64.tar.xz
mv node-v20.18.0-linux-x64 ~/nodejs
echo 'export PATH=$HOME/nodejs/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 2. 安装 Codex CLI

```bash
npm install -g @openai/codex
```

### 3. 验证安装

```bash
codex --version
# 输出: codex-cli 0.77.0 或更高版本
```

## 配置智谱 API

### 1. 设置环境变量

```bash
# 临时设置
export ZHIPU_API_KEY="你的智谱API_KEY"

# 永久设置（添加到 ~/.bashrc）
echo 'export ZHIPU_API_KEY="你的智谱API_KEY"' >> ~/.bashrc
source ~/.bashrc
```

### 2. 创建配置文件

创建 `~/.codex/config.toml`:

```bash
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
EOF
```

## 配置说明

| 配置项 | 说明 |
|--------|------|
| `name` | Provider 显示名称 |
| `base_url` | 智谱 Coding API 端点 |
| `env_key` | 存储 API Key 的环境变量名 |
| `wire_api` | API 协议类型，使用 `chat` |

## 可用模型

| 模型 | 说明 |
|------|------|
| `glm-4.7` | 最新旗舰模型，358B MoE 架构 |
| `glm-4.6` | 355B MoE 架构，200K 上下文 |
| `glm-4.5-air` | 轻量版本 |

## 使用方法

### 交互模式

```bash
# 进入交互模式
codex -c model_provider=zhipu -c model=glm-4.7

# 带初始提示进入
codex -c model_provider=zhipu -c model=glm-4.7 "帮我分析这个项目"
```

### 非交互模式

```bash
# 使用 exec 子命令
echo "你的问题" | codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto

# 带提示参数
codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto "帮我写一个 Hello World"
```

### 常用参数

| 参数 | 说明 |
|------|------|
| `-c key=value` | 覆盖配置项 |
| `-m, --model` | 指定模型 |
| `--full-auto` | 自动执行所有操作 |
| `-a, --ask-for-approval` | 设置审批策略 |
| `--version` | 显示版本 |

### 审批策略

| 策略 | 说明 |
|------|------|
| `untrusted` | 仅运行受信任命令 |
| `on-failure` | 失败时询问 |
| `on-request` | 模型请求时询问 |
| `never` | 从不询问（需配合 --full-auto） |

### 继续之前的对话

```bash
# 继续最近的对话
codex resume --last

# 打开会话选择器
codex resume

# 指定会话 ID 恢复
codex resume <session-id>

# 显示所有会话（包括其他目录）
codex resume --all

# 恢复时使用智谱配置
codex resume --last -c model_provider=zhipu -c model=glm-4.7
```

## 测试验证

```bash
cd /tmp && mkdir -p codex-test && cd codex-test && git init
echo "回复：你好" | codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto
```

预期输出：
```
--------
model: glm-4.7
provider: zhipu
--------
你好！很高兴见到你。有什么我可以帮助你的吗？
```

> 注意：Codex 需要在 Git 仓库目录下运行

## 故障排除

### 404 Not Found 错误

确保 `wire_api` 设置为 `chat`，而非 `responses`（智谱暂不支持 responses API）。

### "Not inside a trusted directory" 错误

Codex 需要在 Git 仓库中运行：
```bash
git init
```

### 环境变量未生效

重新打开终端，或执行 `source ~/.bashrc`。

### deprecation 警告

`Support for the "chat" wire API is deprecated` 警告可忽略，智谱目前仅支持 chat API。

## 参考资料

- [智谱 Coding Plan 官方文档](https://docs.bigmodel.cn/cn/coding-plan/tool/others)
- [Codex CLI 官方文档](https://developers.openai.com/codex/cli/)
- [Codex CLI 配置参考](https://developers.openai.com/codex/config-reference/)
