# Gemini CLI Docker 镜像（定制版）
# 使用智谱 API 的 Gemini CLI 容器化部署
#
# 构建: docker build -t gemini-cli-zhipu .
# 运行: docker run -it --rm -e OPENROUTER_API_KEY=xxx -v $(pwd):/workspace gemini-cli-zhipu

FROM node:20-slim AS builder

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 克隆定制版仓库
WORKDIR /build
RUN git clone https://github.com/heartyguy/gemini-cli . && \
    git checkout feature/openrouter-support

# 修改模型映射（支持 GLM 模型）
RUN sed -i 's/return modelMap\[model\] || `google\/\${model}`;/return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google\/${model}`);/' \
    packages/core/src/core/contentGenerator.ts

# 安装依赖并构建
RUN npm install && npm run build

# 运行阶段
FROM node:20-slim

LABEL maintainer="AI CLI Research"
LABEL description="Gemini CLI (custom fork) with Zhipu API support"

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制
COPY --from=builder /build /opt/gemini-cli

WORKDIR /workspace

# 设置环境变量
ENV OPENROUTER_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node /opt/gemini-cli/packages/cli/dist/index.js --version 2>/dev/null || exit 1

# 入口点 - 默认使用 glm-4.7 模型，不带参数进入交互模式
ENTRYPOINT ["node", "/opt/gemini-cli/packages/cli/dist/index.js", "-m", "glm-4.7"]
CMD []
