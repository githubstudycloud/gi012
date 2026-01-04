#!/bin/bash
# 初始化多分支仓库

set -e

echo "=== 初始化 Multi-AI Orchestrator 仓库 ==="

# 创建数据和日志目录
mkdir -p data logs

# 添加 .gitignore
cat > .gitignore << 'EOF'
# 数据和日志
data/
logs/
*.db
*.log

# Python
__pycache__/
*.pyc
.venv/
venv/

# 敏感信息
*.key
*.pem
secrets/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

echo "=== 仓库初始化完成 ==="
echo ""
echo "下一步操作:"
echo "1. 编辑 config/services/ 下的服务配置"
echo "2. 运行 pip install -r requirements.txt"
echo "3. 复制 skills/ 到 ~/.claude/skills/"
