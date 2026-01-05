#!/bin/bash
#
# 智谱 API 接入 AI CLI 工具一键安装脚本
# 支持: Claude Code, Codex CLI, Gemini CLI
#
# 使用方法:
#   1. 编辑此文件，设置 ZHIPU_API_KEY
#   2. chmod +x install-ai-cli.sh
#   3. ./install-ai-cli.sh
#

set -e

# ============================================
# 配置区域 - 请修改以下变量
# ============================================

# 智谱 API Key（必须替换为你的 Key）
ZHIPU_API_KEY="YOUR_API_KEY"

# ============================================
# 以下内容无需修改
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 API Key
if [ "$ZHIPU_API_KEY" = "YOUR_API_KEY" ]; then
    log_error "请先编辑脚本，设置你的 ZHIPU_API_KEY"
    log_info "获取 API Key: https://bigmodel.cn/usercenter/proj-mgmt/apikeys"
    exit 1
fi

echo ""
echo "=========================================="
echo "  智谱 API 接入 AI CLI 工具安装脚本"
echo "=========================================="
echo ""

# 1. 安装 Node.js
log_info "正在安装 Node.js v20.18.0..."
cd ~

if [ -d "$HOME/nodejs" ]; then
    log_warn "Node.js 已存在，跳过安装"
else
    wget -q --show-progress https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz
    tar -xf node-v20.18.0-linux-x64.tar.xz
    mv node-v20.18.0-linux-x64 ~/nodejs
    rm -f node-v20.18.0-linux-x64.tar.xz
fi

export PATH=$HOME/nodejs/bin:$PATH

# 检查是否已在 bashrc 中
if ! grep -q 'nodejs/bin' ~/.bashrc; then
    echo 'export PATH=$HOME/nodejs/bin:$PATH' >> ~/.bashrc
fi

log_info "Node.js 版本: $(node --version)"

# 2. 安装 Claude Code
log_info "正在安装 Claude Code..."
npm install -g @anthropic-ai/claude-code --silent 2>/dev/null || npm install -g @anthropic-ai/claude-code

# 3. 配置 Claude Code
log_info "正在配置 Claude Code..."
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

log_info "Claude Code 版本: $(claude --version)"

# 4. 安装 Codex CLI
log_info "正在安装 Codex CLI..."
npm install -g @openai/codex --silent 2>/dev/null || npm install -g @openai/codex

# 5. 配置 Codex CLI
log_info "正在配置 Codex CLI..."
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
EOF

# 设置环境变量
export ZHIPU_API_KEY="$ZHIPU_API_KEY"
if ! grep -q 'ZHIPU_API_KEY' ~/.bashrc; then
    echo "export ZHIPU_API_KEY=\"$ZHIPU_API_KEY\"" >> ~/.bashrc
fi

log_info "Codex CLI 版本: $(codex --version)"

# 6. 安装 Gemini CLI（定制版）
log_info "正在安装 Gemini CLI（定制版）..."
cd ~

if [ -d "$HOME/gemini-cli-zhipu" ]; then
    log_warn "Gemini CLI 目录已存在，正在更新..."
    cd ~/gemini-cli-zhipu
    git fetch origin
    git checkout feature/openrouter-support
    git pull origin feature/openrouter-support 2>/dev/null || true
else
    git clone https://github.com/heartyguy/gemini-cli gemini-cli-zhipu
    cd ~/gemini-cli-zhipu
    git checkout feature/openrouter-support
fi

# 7. 修改模型映射
log_info "正在修改模型映射..."
CONTENT_FILE="packages/core/src/core/contentGenerator.ts"
if grep -q "model.toLowerCase().startsWith" "$CONTENT_FILE"; then
    log_warn "模型映射已修改，跳过"
else
    sed -i 's/return modelMap\[model\] || `google\/\${model}`;/return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google\/${model}`);/' \
        "$CONTENT_FILE"
fi

# 8. 安装依赖并构建
log_info "正在安装依赖并构建（可能需要几分钟）..."
npm install --silent 2>/dev/null || npm install
npm run build --silent 2>/dev/null || npm run build

# 9. 配置 Gemini CLI 环境变量
log_info "正在配置 Gemini CLI 环境变量..."
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="$ZHIPU_API_KEY"

if ! grep -q 'OPENROUTER_BASE_URL' ~/.bashrc; then
    cat >> ~/.bashrc << EOF
export OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
export OPENROUTER_API_KEY="$ZHIPU_API_KEY"
alias gemini="node ~/gemini-cli-zhipu/packages/cli/dist/index.js"
EOF
fi

log_info "Gemini CLI: 定制版安装完成"

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "请执行以下命令加载环境变量："
echo "  source ~/.bashrc"
echo ""
echo "测试命令："
echo "  echo '你好' | claude -p"
echo "  cd /tmp && mkdir -p test && cd test && git init && echo '你好' | codex exec -c model_provider=zhipu -c model=glm-4.7 --full-auto"
echo "  echo '你好' | gemini -m glm-4.7 -p 2>/dev/null"
echo ""
