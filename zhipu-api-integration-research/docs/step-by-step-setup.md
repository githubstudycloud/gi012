# 智谱 API 接入完整操作记录

本文档记录了在 Ubuntu 22.04 服务器上实际执行的所有命令，可直接复制执行。

## 前置条件

- Ubuntu 22.04 LTS 服务器
- 智谱 API Key（从 https://bigmodel.cn/usercenter/proj-mgmt/apikeys 获取）
- 网络可访问 `open.bigmodel.cn`

---

## 第一步：安装 Node.js（无需 sudo）

```bash
# 下载 Node.js v20.18.0
cd ~
wget https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz

# 解压
tar -xf node-v20.18.0-linux-x64.tar.xz

# 移动到 ~/nodejs
mv node-v20.18.0-linux-x64 ~/nodejs

# 添加到 PATH
echo 'export PATH=$HOME/nodejs/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# 验证安装
node --version
# 预期输出: v20.18.0

npm --version
# 预期输出: 10.8.2
```

---

## 第二步：安装 Claude Code

```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 验证安装
claude --version
# 预期输出: 2.0.76 (Claude Code)
```

---

## 第三步：配置 Claude Code

```bash
# 创建配置目录
mkdir -p ~/.claude

# 创建配置文件（替换 YOUR_API_KEY 为你的智谱 API Key）
cat > ~/.claude/settings.json << 'EOF'
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "YOUR_API_KEY",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
EOF

# 验证配置文件
cat ~/.claude/settings.json
```

---

## 第四步：测试 Claude Code

```bash
# 测试（应该返回模型响应）
echo "回复：测试成功" | claude -p

# 预期输出类似：
# 太好了！测试成功。很高兴看到一切运行正常。
```

---

## 第五步：安装 Codex CLI

```bash
# 安装 Codex CLI
npm install -g @openai/codex

# 验证安装
codex --version
# 预期输出: codex-cli 0.77.0
```

---

## 第六步：配置 Codex CLI

```bash
# 创建配置目录
mkdir -p ~/.codex

# 创建配置文件
cat > ~/.codex/config.toml << 'EOF'
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
EOF

# 验证配置文件
cat ~/.codex/config.toml

# 设置环境变量（替换 YOUR_API_KEY）
export ZHIPU_API_KEY="YOUR_API_KEY"

# 永久保存环境变量
echo 'export ZHIPU_API_KEY="YOUR_API_KEY"' >> ~/.bashrc
source ~/.bashrc
```

---

## 第七步：测试 Codex CLI

```bash
# Codex 需要在 Git 仓库中运行
cd /tmp
mkdir -p codex-test
cd codex-test
git init

# 测试
echo "回复：测试成功" | codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto

# 预期输出类似：
# --------
# model: glm-4.7
# provider: zhipu
# --------
# 很高兴听到测试成功！有什么我可以帮您的吗？
```

---

## 第八步：安装 Gemini CLI（定制版）

```bash
# 克隆定制版仓库
cd ~
git clone https://github.com/heartyguy/gemini-cli gemini-cli-zhipu
cd gemini-cli-zhipu

# 切换到兼容分支
git checkout feature/openrouter-support

# 安装依赖（可能需要几分钟）
npm install
```

---

## 第九步：修改模型映射

```bash
# 编辑文件 packages/core/src/core/contentGenerator.ts
# 找到第 38 行左右的 mapGeminiModelToOpenRouter 函数

# 使用 sed 自动修改（推荐）
sed -i 's/return modelMap\[model\] || `google\/\${model}`;/return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google\/${model}`);/' \
    packages/core/src/core/contentGenerator.ts

# 或者手动编辑：
# 原代码: return modelMap[model] || `google/${model}`;
# 改为:   return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google/${model}`);
```

---

## 第十步：构建 Gemini CLI

```bash
# 构建项目
cd ~/gemini-cli-zhipu
npm run build

# 验证构建成功
ls packages/cli/dist/index.js
```

---

## 第十一步：配置 Gemini CLI 环境变量

```bash
# 设置环境变量（替换 YOUR_API_KEY）
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="YOUR_API_KEY"

# 永久保存
cat >> ~/.bashrc << 'EOF'
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="YOUR_API_KEY"
EOF
source ~/.bashrc
```

---

## 第十二步：测试 Gemini CLI

```bash
# 测试（2>/dev/null 隐藏 telemetry 警告）
cd ~/gemini-cli-zhipu
echo "回复：测试成功" | node packages/cli/dist/index.js -m glm-4.7 -p 2>/dev/null

# 预期输出类似：
# 收到明白。
```

---

## 第十三步：创建便捷别名（可选）

```bash
# 添加 Gemini CLI 别名
echo 'alias gemini="node ~/gemini-cli-zhipu/packages/cli/dist/index.js"' >> ~/.bashrc
source ~/.bashrc

# 使用别名
gemini -m glm-4.7 -p "你好"
```

---

## 完整一键安装脚本

将以下内容保存为 `install-ai-cli.sh`：

```bash
#!/bin/bash

# 智谱 API Key（必须替换）
ZHIPU_API_KEY="YOUR_API_KEY"

# 检查 API Key
if [ "$ZHIPU_API_KEY" = "YOUR_API_KEY" ]; then
    echo "错误：请先编辑脚本，设置你的 ZHIPU_API_KEY"
    exit 1
fi

echo "=== 开始安装 ==="

# 1. 安装 Node.js
echo ">>> 安装 Node.js..."
cd ~
wget -q https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz
tar -xf node-v20.18.0-linux-x64.tar.xz
mv node-v20.18.0-linux-x64 ~/nodejs
rm node-v20.18.0-linux-x64.tar.xz
export PATH=$HOME/nodejs/bin:$PATH
echo 'export PATH=$HOME/nodejs/bin:$PATH' >> ~/.bashrc

# 2. 安装 Claude Code
echo ">>> 安装 Claude Code..."
npm install -g @anthropic-ai/claude-code

# 3. 配置 Claude Code
mkdir -p ~/.claude
cat > ~/.claude/settings.json << EOF
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "$ZHIPU_API_KEY",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
EOF

# 4. 安装 Codex CLI
echo ">>> 安装 Codex CLI..."
npm install -g @openai/codex

# 5. 配置 Codex CLI
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
EOF

# 6. 设置环境变量
export ZHIPU_API_KEY="$ZHIPU_API_KEY"
echo "export ZHIPU_API_KEY=\"$ZHIPU_API_KEY\"" >> ~/.bashrc

# 7. 安装 Gemini CLI
echo ">>> 安装 Gemini CLI..."
cd ~
git clone -q https://github.com/heartyguy/gemini-cli gemini-cli-zhipu
cd gemini-cli-zhipu
git checkout -q feature/openrouter-support

# 8. 修改模型映射
sed -i 's/return modelMap\[model\] || `google\/\${model}`;/return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google\/${model}`);/' \
    packages/core/src/core/contentGenerator.ts

# 9. 安装依赖并构建
npm install --silent
npm run build --silent

# 10. 配置 Gemini CLI 环境变量
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="$ZHIPU_API_KEY"
cat >> ~/.bashrc << EOF
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="$ZHIPU_API_KEY"
alias gemini="node ~/gemini-cli-zhipu/packages/cli/dist/index.js"
EOF

echo "=== 安装完成 ==="
echo ""
echo "请执行: source ~/.bashrc"
echo ""
echo "测试命令："
echo "  claude --version"
echo "  codex --version"
echo "  echo '你好' | claude -p"
```

---

## 快速验证

```bash
# 重新加载环境变量
source ~/.bashrc

# 验证安装
echo "=== 版本信息 ==="
claude --version
codex --version
node ~/gemini-cli-zhipu/packages/cli/dist/index.js --version 2>/dev/null || echo "Gemini CLI: 定制版"

# 测试三个工具
echo ""
echo "=== 测试 Claude Code ==="
echo "你好" | claude -p

echo ""
echo "=== 测试 Codex CLI ==="
cd /tmp && mkdir -p test-codex && cd test-codex && git init -q
echo "你好" | codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto 2>/dev/null

echo ""
echo "=== 测试 Gemini CLI ==="
cd ~/gemini-cli-zhipu
echo "你好" | node packages/cli/dist/index.js -m glm-4.7 -p 2>/dev/null
```

---

## 常用命令速查

| 工具 | 交互模式 | 非交互模式 | 继续对话 |
|------|----------|------------|----------|
| Claude Code | `claude` | `echo "问题" \| claude -p` | `claude -c` |
| Codex CLI | `codex -c model_provider=zhipu -c model=glm-4.7` | `echo "问题" \| codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto` | `codex resume --last` |
| Gemini CLI | `gemini -m glm-4.7` | `echo "问题" \| gemini -m glm-4.7 -p 2>/dev/null` | 不支持 |

---

## 故障排除

### 命令找不到

```bash
# 确保 PATH 正确
source ~/.bashrc
echo $PATH | grep nodejs
```

### Codex 报错 "Not inside a trusted directory"

```bash
# 进入 Git 仓库
cd /path/to/your/project
git init  # 如果不是 Git 仓库
```

### Gemini CLI telemetry 超时警告

```bash
# 这是正常的，使用 2>/dev/null 隐藏
echo "问题" | gemini -m glm-4.7 -p 2>/dev/null
```

### API 连接超时

```bash
# 测试网络连通性
curl -I https://open.bigmodel.cn
```
