# Claude Code Docker 镜像
# 使用智谱 API 的 Claude Code 容器化部署
#
# 构建: docker build -t claude-code-zhipu .
# 运行: docker run -it --rm -v $(pwd):/workspace claude-code-zhipu

FROM node:20-slim

LABEL maintainer="AI CLI Research"
LABEL description="Claude Code with Zhipu API support"

# 安装必要工具
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Claude Code
RUN npm install -g @anthropic-ai/claude-code

# 创建配置目录
RUN mkdir -p /root/.claude

# 创建工作目录
WORKDIR /workspace

# 默认配置模板（运行时会被挂载覆盖）
RUN echo '{\n\
  "env": {\n\
    "ANTHROPIC_AUTH_TOKEN": "YOUR_API_KEY",\n\
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",\n\
    "API_TIMEOUT_MS": "3000000",\n\
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"\n\
  }\n\
}' > /root/.claude/settings.json

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD claude --version || exit 1

# 入口点
ENTRYPOINT ["claude"]
CMD ["--help"]
