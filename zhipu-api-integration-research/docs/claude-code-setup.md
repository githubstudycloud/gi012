# Claude Code 接入智谱 GLM 安装配置指南

## 概述

Claude Code 是 Anthropic 官方的 CLI 编程助手。智谱提供了兼容 Anthropic API 格式的端点，可以直接使用 GLM 模型。

## 系统要求

- Node.js >= 18.x
- npm >= 8.x

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

### 2. 安装 Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 3. 验证安装

```bash
claude --version
# 输出: 2.0.76 (Claude Code) 或更高版本
```

## 配置智谱 API

### 方法 1：使用官方助手（推荐）

```bash
npx @z_ai/coding-helper
```

按提示输入 API Key 即可自动完成配置。

### 方法 2：手动配置

创建或编辑配置文件 `~/.claude/settings.json`:

```bash
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "你的智谱API_KEY",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
EOF
```

## 配置说明

| 配置项 | 说明 |
|--------|------|
| `ANTHROPIC_AUTH_TOKEN` | 智谱 API Key，从[智谱开放平台](https://bigmodel.cn/usercenter/proj-mgmt/apikeys)获取 |
| `ANTHROPIC_BASE_URL` | 智谱 Anthropic 兼容端点 |
| `API_TIMEOUT_MS` | 请求超时时间（毫秒） |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | 禁用非必要网络请求 |

## 模型映射

智谱会自动将 Claude 模型映射到 GLM 模型：

| Claude 模型 | 智谱模型 |
|-------------|----------|
| claude-3-opus | GLM-4.7 |
| claude-3-sonnet | GLM-4.7 |
| claude-3-haiku | GLM-4.5-Air |

## 使用方法

### 交互模式

```bash
claude
```

### 非交互模式

```bash
# 使用管道输入
echo "你的问题" | claude -p

# 使用参数输入
claude -p "帮我写一个 Python Hello World"
```

### 常用参数

| 参数 | 说明 |
|------|------|
| `-p, --print` | 非交互模式，输出结果后退出 |
| `-c, --continue` | 继续最近的对话 |
| `-r, --resume` | 恢复历史会话（打开选择器） |
| `--version` | 显示版本 |
| `--help` | 显示帮助 |

### 继续之前的对话

```bash
# 继续最近的对话
claude -c
claude --continue

# 打开会话选择器（可搜索）
claude -r
claude --resume

# 指定会话 ID 恢复
claude -r <session-id>

# 恢复但创建新分支（不修改原会话）
claude -r --fork-session
```

## 测试验证

```bash
echo "回复：你好" | claude -p
```

预期输出：
```
你好！很高兴见到你。有什么我可以帮助你的吗？
```

## 故障排除

### 连接超时

检查网络连接，确保可以访问 `open.bigmodel.cn`。

### API Key 错误

确保 API Key 正确，格式为：`xxxxxxxx.xxxxxxxx`

### 配置未生效

重新打开终端，或执行 `source ~/.bashrc`。

## 参考资料

- [智谱 Claude Code 官方文档](https://docs.bigmodel.cn/cn/coding-plan/tool/claude)
- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [Claude Code GitHub](https://github.com/anthropics/claude-code)
