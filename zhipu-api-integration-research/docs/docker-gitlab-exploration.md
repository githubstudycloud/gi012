# Docker 安装与 GitLab 自建探究文档

## 概述

本文档记录在 Ubuntu 22.04 服务器上使用 Docker 部署 AI CLI 工具和自建 GitLab 的探究过程。

---

## Docker 安装

### 方法 1：官方安装脚本（推荐）

```bash
# 需要 sudo 权限
curl -fsSL https://get.docker.com | sudo sh

# 将当前用户加入 docker 组（避免每次使用 sudo）
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker compose version
```

### 方法 2：手动安装

```bash
# 1. 更新包索引
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg

# 2. 添加 Docker 官方 GPG 密钥
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 3. 添加仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. 安装 Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 方法 3：Snap 安装

```bash
sudo snap install docker
```

---

## AI CLI 工具 Docker 镜像

### Claude Code

#### 官方 Docker 沙箱镜像

Docker 与 Anthropic 合作提供了官方沙箱镜像：

```bash
# 使用官方沙箱模板
docker run -it --rm \
  -v "$(pwd)":/workspace \
  -w /workspace \
  docker/sandbox-templates:claude-code
```

**特点**：
- 自动凭据管理（首次运行提示输入 API Key）
- 凭据存储在持久卷 `docker-claude-sandbox-data`
- 预装 Docker CLI、GitHub CLI、Node.js、Go、Python 3、Git、ripgrep、jq

#### 社区镜像

```bash
# gendosu/claude-code-docker
docker pull gendosu/claude-code-docker
docker run -it --rm gendosu/claude-code-docker
```

#### 自建 Dockerfile

```dockerfile
FROM node:20-slim

# 安装 Claude Code
RUN npm install -g @anthropic-ai/claude-code

# 创建配置目录
RUN mkdir -p /root/.claude

# 设置工作目录
WORKDIR /workspace

# 配置智谱 API（运行时挂载或设置环境变量）
# ENV ANTHROPIC_AUTH_TOKEN=your-key
# ENV ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic

ENTRYPOINT ["claude"]
```

**构建与运行**：

```bash
# 构建
docker build -t claude-code-zhipu .

# 运行（挂载配置文件）
docker run -it --rm \
  -v ~/.claude:/root/.claude \
  -v "$(pwd)":/workspace \
  claude-code-zhipu
```

### Codex CLI

#### 官方镜像

OpenAI 提供了 `codex-universal` 镜像：

```bash
# 使用官方镜像
docker run --rm -it \
  -e CODEX_ENV_RUST_VERSION=1.87.0 \
  -v "$(pwd)":/workspace/"$(basename "$(pwd)")" \
  -w /workspace/"$(basename "$(pwd)")" \
  ghcr.io/openai/codex-universal:latest
```

**特点**：
- 多语言开发环境
- 可自定义语言版本
- 包含常用开发工具

#### 自建 Dockerfile（智谱配置）

```dockerfile
FROM node:22-slim

# 安装 Git（Codex 需要）
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 安装 Codex CLI
RUN npm install -g @openai/codex

# 创建配置目录
RUN mkdir -p /root/.codex

# 复制配置文件
COPY config.toml /root/.codex/config.toml

WORKDIR /workspace

ENTRYPOINT ["codex"]
```

**config.toml**：

```toml
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
```

**构建与运行**：

```bash
# 构建
docker build -t codex-zhipu .

# 运行
docker run -it --rm \
  -e ZHIPU_API_KEY=your-api-key \
  -v "$(pwd)":/workspace \
  codex-zhipu -c model_provider=zhipu -c model=glm-4.7
```

### Gemini CLI

#### 官方沙箱镜像

Google 提供了 `gemini-cli-sandbox` 镜像用于安全隔离执行：

```bash
# 官方仓库包含 Dockerfile
git clone https://github.com/google-gemini/gemini-cli
cd gemini-cli
docker build -t gemini-cli-sandbox .
```

#### 社区镜像

```bash
# naoyoshinori/gemini-cli
docker pull naoyoshinori/gemini-cli
docker run -it --rm \
  -e GOOGLE_API_KEY=your-key \
  naoyoshinori/gemini-cli

# tgagor/docker-gemini-cli（自动更新）
docker pull tgagor/gemini-cli
```

#### 自建 Dockerfile（智谱配置）

由于需要使用定制版，需要从源码构建：

```dockerfile
FROM node:20-slim

# 安装 Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 克隆定制版仓库
RUN git clone https://github.com/heartyguy/gemini-cli /opt/gemini-cli
WORKDIR /opt/gemini-cli

# 切换分支
RUN git checkout feature/openrouter-support

# 安装依赖
RUN npm install

# 修改模型映射（使用 sed）
RUN sed -i 's/return modelMap\[model\] || `google\/\${model}`;/return modelMap[model] || (model.toLowerCase().startsWith("glm") ? model : `google\/${model}`);/' \
    packages/core/src/core/contentGenerator.ts

# 构建
RUN npm run build

WORKDIR /workspace

ENTRYPOINT ["node", "/opt/gemini-cli/packages/cli/dist/index.js"]
```

**构建与运行**：

```bash
# 构建
docker build -t gemini-cli-zhipu .

# 运行
docker run -it --rm \
  -e OPENROUTER_BASE_URL=https://open.bigmodel.cn/api/coding/paas/v4 \
  -e OPENROUTER_API_KEY=your-api-key \
  -v "$(pwd)":/workspace \
  gemini-cli-zhipu -m glm-4.7
```

---

## 一体化 Docker Compose

创建 `docker-compose.yml` 同时管理三个 CLI 工具：

```yaml
version: '3.8'

services:
  claude-code:
    build:
      context: ./docker/claude-code
    volumes:
      - ./workspace:/workspace
      - claude-config:/root/.claude
    environment:
      - ANTHROPIC_AUTH_TOKEN=${ZHIPU_API_KEY}
      - ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
      - API_TIMEOUT_MS=3000000
      - CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
    stdin_open: true
    tty: true

  codex-cli:
    build:
      context: ./docker/codex-cli
    volumes:
      - ./workspace:/workspace
      - codex-config:/root/.codex
    environment:
      - ZHIPU_API_KEY=${ZHIPU_API_KEY}
    stdin_open: true
    tty: true

  gemini-cli:
    build:
      context: ./docker/gemini-cli
    volumes:
      - ./workspace:/workspace
    environment:
      - OPENROUTER_BASE_URL=https://open.bigmodel.cn/api/coding/paas/v4
      - OPENROUTER_API_KEY=${ZHIPU_API_KEY}
    stdin_open: true
    tty: true

volumes:
  claude-config:
  codex-config:
```

**使用方法**：

```bash
# 设置 API Key
export ZHIPU_API_KEY=your-api-key

# 构建所有镜像
docker compose build

# 运行 Claude Code
docker compose run --rm claude-code

# 运行 Codex CLI
docker compose run --rm codex-cli -c model_provider=zhipu -c model=glm-4.7

# 运行 Gemini CLI
docker compose run --rm gemini-cli -m glm-4.7
```

---

## GitLab 自建

### 系统要求

- 最少 4GB 内存
- 有效的外部可访问主机名或 IP
- Docker 和 Docker Compose

### 快速部署（Docker Compose）

创建 `gitlab-docker-compose.yml`：

```yaml
version: '3.8'

services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    restart: always
    hostname: 'gitlab.example.com'  # 替换为你的域名或 IP
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://gitlab.example.com'
        # 修改 SSH 端口避免冲突
        gitlab_rails['gitlab_shell_ssh_port'] = 2222
    ports:
      - '80:80'
      - '443:443'
      - '2222:22'
    volumes:
      - gitlab-config:/etc/gitlab
      - gitlab-logs:/var/log/gitlab
      - gitlab-data:/var/opt/gitlab
    shm_size: '256m'

volumes:
  gitlab-config:
  gitlab-logs:
  gitlab-data:
```

**部署步骤**：

```bash
# 1. 创建目录
mkdir -p ~/gitlab && cd ~/gitlab

# 2. 创建 docker-compose.yml（内容如上）

# 3. 启动 GitLab
docker compose up -d

# 4. 查看日志（初始化需要 10-30 分钟）
docker compose logs -f gitlab

# 5. 获取初始 root 密码（24小时内有效）
docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

### 单命令部署

```bash
sudo docker run --detach \
  --hostname YOUR_SERVER_IP \
  --publish 443:443 --publish 80:80 --publish 2222:22 \
  --name gitlab \
  --restart always \
  --volume /srv/gitlab/config:/etc/gitlab \
  --volume /srv/gitlab/logs:/var/log/gitlab \
  --volume /srv/gitlab/data:/var/opt/gitlab \
  --shm-size 256m \
  gitlab/gitlab-ce:latest
```

### 首次登录

1. 访问 `http://YOUR_SERVER_IP`
2. 用户名：`root`
3. 密码：使用上面命令获取的初始密码
4. **立即修改密码**（初始密码 24 小时后失效）

### 用于配置管理

创建仓库存储 CLI 配置：

```bash
# 1. 创建新项目：ai-cli-configs

# 2. 克隆到本地
git clone http://YOUR_GITLAB_IP/root/ai-cli-configs.git
cd ai-cli-configs

# 3. 添加配置文件
mkdir -p claude codex gemini

# Claude Code 配置
cat > claude/settings.json << 'EOF'
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "${ZHIPU_API_KEY}",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
EOF

# Codex CLI 配置
cat > codex/config.toml << 'EOF'
[model_providers.zhipu]
name = "Zhipu AI Coding"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
env_key = "ZHIPU_API_KEY"
wire_api = "chat"
EOF

# 4. 提交
git add .
git commit -m "Add AI CLI configurations"
git push origin main
```

### 配置同步脚本

创建 `sync-configs.sh`：

```bash
#!/bin/bash
# 同步 AI CLI 配置

GITLAB_URL="http://YOUR_GITLAB_IP"
REPO="root/ai-cli-configs"
BRANCH="main"

# 临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 克隆配置仓库
git clone --depth 1 -b $BRANCH "$GITLAB_URL/$REPO.git" "$TEMP_DIR"

# 同步 Claude Code 配置
mkdir -p ~/.claude
cp "$TEMP_DIR/claude/settings.json" ~/.claude/

# 同步 Codex CLI 配置
mkdir -p ~/.codex
cp "$TEMP_DIR/codex/config.toml" ~/.codex/

echo "配置同步完成！"
```

---

## 探究记录

### 环境信息

- **操作系统**: Ubuntu 22.04.5 LTS
- **内核**: 5.15.0-164-generic
- **用户**: ubuntu (uid=1000, gid=1000)
- **用户组**: ubuntu, adm, cdrom, sudo, dip, plugdev, lxd

### 探究过程

1. **Docker 可用性检查**：服务器未安装 Docker
2. **Sudo 权限**：用户在 sudo 组但需要密码
3. **替代方案**：
   - Snap 可用但安装 Docker 仍需 sudo
   - LXD 可用，可作为容器替代方案
   - Podman 未安装

### 结论

在没有 sudo 密码的环境下：
- 无法直接安装 Docker
- 可以使用 LXD 作为替代（用户已在 lxd 组）
- 本地开发可使用手动安装方式（已完成）

### 推荐方案

1. **有 sudo 权限**：使用 Docker + GitLab CE 方案
2. **无 sudo 权限**：使用手动安装 + Git 远程仓库同步配置
3. **企业环境**：使用 GitLab EE + Docker Registry 统一管理

---

## 参考资料

### Docker 相关
- [Docker 官方文档](https://docs.docker.com/)
- [Docker + Claude Code](https://docs.docker.com/ai/sandboxes/claude-code/)
- [OpenAI Codex Universal](https://github.com/openai/codex-universal)
- [Gemini CLI Dockerfile](https://github.com/google-gemini/gemini-cli/blob/main/Dockerfile)

### GitLab 相关
- [GitLab Docker 安装文档](https://docs.gitlab.com/install/docker/installation/)
- [sameersbn/docker-gitlab](https://github.com/sameersbn/docker-gitlab)

### 社区镜像
- [gendosu/claude-code-docker](https://hub.docker.com/r/gendosu/claude-code-docker)
- [naoyoshinori/gemini-cli](https://hub.docker.com/r/naoyoshinori/gemini-cli)
- [tgagor/docker-gemini-cli](https://github.com/tgagor/docker-gemini-cli)
