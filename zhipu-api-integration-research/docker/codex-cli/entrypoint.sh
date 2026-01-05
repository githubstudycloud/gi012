#!/bin/bash
# Codex CLI 入口点脚本
# 确保工作目录是 Git 仓库

# 如果不是 Git 仓库，初始化一个
if [ ! -d ".git" ]; then
    git init -q
fi

# 执行 Codex CLI
exec codex -c model_provider=zhipu -c model=glm-4.7 "$@"
