# Gemini CLI 接入智谱 GLM 安装配置指南

## 概述

Gemini CLI 是 Google 官方的命令行 AI 助手。由于官方版本仅支持 Google Gemini 模型，需要使用**定制版**才能接入智谱 GLM 模型。

## 系统要求

- Node.js >= 18.x
- npm >= 8.x
- Git

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

### 2. 克隆定制版仓库

```bash
git clone https://github.com/heartyguy/gemini-cli
cd gemini-cli
```

### 3. 切换到兼容分支

```bash
git checkout feature/openrouter-support
```

### 4. 安装依赖

```bash
npm install
```

### 5. 修改模型映射（重要！）

编辑 `packages/core/src/core/contentGenerator.ts`，找到 `mapGeminiModelToOpenRouter` 函数（约第 23-39 行），修改返回语句：

```typescript
// 原代码（约第 38 行）
return modelMap[model] || `google/${model}`;

// 改为（支持 GLM 模型）
return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google/${model}`);
```

### 6. 构建项目

```bash
npm run build
```

## 配置智谱 API

### 设置环境变量

```bash
# 临时设置
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="你的智谱API_KEY"

# 永久设置（添加到 ~/.bashrc）
cat >> ~/.bashrc << 'EOF'
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="你的智谱API_KEY"
EOF
source ~/.bashrc
```

## 配置说明

| 环境变量 | 说明 |
|----------|------|
| `OPENROUTER_BASE_URL` | 智谱 Coding API 端点 |
| `OPENROUTER_API_KEY` | 智谱 API Key |

## 可用模型

| 模型 | 说明 |
|------|------|
| `glm-4.7` | 最新旗舰模型，358B MoE 架构 |
| `glm-4.6` | 355B MoE 架构，200K 上下文 |
| `glm-4.5-air` | 轻量版本 |

## 使用方法

### 基本用法

```bash
# 进入项目目录
cd ~/gemini-cli

# 交互模式
node packages/cli/dist/index.js -m glm-4.7

# 非交互模式（使用管道）
echo "你的问题" | node packages/cli/dist/index.js -m glm-4.7 -p 2>/dev/null
```

### 创建别名（推荐）

```bash
# 添加到 ~/.bashrc
echo 'alias gemini="node ~/gemini-cli/packages/cli/dist/index.js"' >> ~/.bashrc
source ~/.bashrc

# 使用别名
gemini -m glm-4.7 -p "你的问题"
```

### 常用参数

| 参数 | 说明 |
|------|------|
| `-m, --model` | 指定模型（必须指定 glm-4.7 等） |
| `-p, --prompt` | 提示内容 |
| `-y, --yolo` | 自动接受所有操作 |
| `-d, --debug` | 调试模式 |
| `--version` | 显示版本 |

### 会话恢复

> **注意**: 定制版 Gemini CLI **暂不支持**会话恢复功能。每次运行都是新会话。

## 测试验证

```bash
cd ~/gemini-cli
echo "回复：你好" | node packages/cli/dist/index.js -m glm-4.7 -p 2>/dev/null
```

预期输出：
```
你好！有什么我可以帮你的吗？
```

> 注意：`2>/dev/null` 用于隐藏 telemetry 超时警告

## 故障排除

### "模型不存在" 错误

确保已修改 `contentGenerator.ts` 中的模型映射代码，并重新构建：
```bash
npm run build
```

### Telemetry 超时警告

这是因为无法连接 Google 的遥测服务器，不影响正常使用。使用 `2>/dev/null` 重定向隐藏。

### 环境变量未生效

重新打开终端，或执行 `source ~/.bashrc`。

### npm install 超时

网络问题，可尝试使用镜像：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

## 与官方版本的区别

| 特性 | 官方版 | 定制版 |
|------|--------|--------|
| Google Gemini | ✅ 支持 | ✅ 支持 |
| 智谱 GLM | ❌ 不支持 | ✅ 支持 |
| OpenRouter | ❌ 不支持 | ✅ 支持 |
| npm 安装 | ✅ 支持 | ❌ 需源码构建 |

## 参考资料

- [智谱 Gemini CLI 官方文档](https://docs.bigmodel.cn/cn/guide/develop/gemini)
- [定制版 Gemini CLI GitHub](https://github.com/heartyguy/gemini-cli)
- [官方 Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
