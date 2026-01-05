# Codex CLI Docker 镜像
# 使用智谱 API 的 Codex CLI 容器化部署
#
# 构建: docker build -t codex-cli-zhipu .
# 运行: docker run -it --rm -e ZHIPU_API_KEY=xxx -v $(pwd):/workspace codex-cli-zhipu

FROM node:22-slim

LABEL maintainer="AI CLI Research"
LABEL description="OpenAI Codex CLI with Zhipu API support"

# 安装必要工具
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Codex CLI
RUN npm install -g @openai/codex

# 创建配置目录
RUN mkdir -p /root/.codex

# 创建配置文件
RUN echo '[model_providers.zhipu]\n\
name = "Zhipu AI Coding"\n\
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"\n\
env_key = "ZHIPU_API_KEY"\n\
wire_api = "chat"' > /root/.codex/config.toml

# 创建工作目录并初始化 Git（Codex 需要）
WORKDIR /workspace
RUN git config --global init.defaultBranch main && \
    git config --global user.email "docker@localhost" && \
    git config --global user.name "Docker User"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD codex --version || exit 1

# 入口点脚本 - 自动初始化 git 并启动 codex
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD []
