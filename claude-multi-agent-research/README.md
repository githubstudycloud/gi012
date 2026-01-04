# Claude Code 多机器/多代理协作研究

> 研究日期：2026-01-04

## 1. 概述

本文档研究如何让多台安装了 Claude Code 的机器互相协作，实现：
- 一个实例指导另一个实例工作
- Supervisor（监督者）负责分配任务和验收测试
- Worker（工作者）执行具体开发任务

## 2. 开源项目对比

| 项目 | 语言 | 特点 | 适用场景 | GitHub |
|------|------|------|---------|--------|
| **claude-flow** | Node.js | 64代理、蜂群智能、MCP支持 | 企业级复杂项目 | [ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) |
| **ccswarm** | Rust | 高性能、Git worktree隔离 | 高并发开发 | [nwiizo/ccswarm](https://github.com/nwiizo/ccswarm) |
| **claude-code-by-agents** | TypeScript | @mentions路由、本地+远程混合 | 简单多机器协作 | [baryhuang/claude-code-by-agents](https://github.com/baryhuang/claude-code-by-agents) |
| **SwarmSDK/claude-swarm** | Ruby | YAML配置、角色委派 | Ruby项目团队 | [parruda/swarm](https://github.com/parruda/swarm) |
| **claude-swarm-mcp** | TypeScript | MCP协议、预置模板 | Claude Desktop集成 | [Mayank1805/claude_swarm_mcp_agent](https://github.com/Mayank1805/claude_swarm_mcp_agent) |

## 3. 方案一：claude-flow（推荐）

### 3.1 简介

claude-flow 是目前最完整的 Claude 多代理编排平台，特点：
- 64 个专业代理
- 蜂群智能（Hive-Mind）架构
- 混合记忆系统（AgentDB + SQLite）
- 原生 Claude Code 支持

### 3.2 安装

```bash
# 前置要求
npm install -g @anthropic-ai/claude-code

# 安装 claude-flow
npx claude-flow@alpha init --force
npx claude-flow@alpha --help
```

### 3.3 多机器配置

**机器 A（Supervisor 监督者）：**

```bash
# 启动蜂群控制器
npx claude-flow@alpha hive-mind wizard

# 或直接启动
npx claude-flow@alpha hive-mind spawn "项目任务描述" --claude
```

**机器 B（Worker 工作者）：**

通过 MCP 协议连接到 Supervisor：

```bash
# 配置 MCP 服务器连接
claude mcp add --transport http supervisor http://machine-a:8080/mcp
```

### 3.4 Supervisor-Worker 模式

在 `swarm.yaml` 中配置：

```yaml
agents:
  supervisor:
    role: "Project Manager"
    capabilities:
      - task_decomposition
      - code_review
      - test_verification
    delegates_to:
      - developer
      - tester

  developer:
    role: "Senior Developer"
    capabilities:
      - code_generation
      - refactoring
    working_directory: "/project/src"

  tester:
    role: "QA Engineer"
    capabilities:
      - test_writing
      - test_execution
      - bug_reporting

workflows:
  development:
    - supervisor: "分析需求，分解任务"
    - developer: "实现功能"
    - tester: "编写和运行测试"
    - supervisor: "验收测试结果"
```

### 3.5 使用示例

```bash
# 快速任务（Swarm 模式）
npx claude-flow@alpha swarm "构建 REST API 并测试" --claude

# 复杂项目（Hive-Mind 模式）
npx claude-flow@alpha hive-mind spawn "构建电商系统：
- Supervisor: 分解任务、代码审查、验收测试
- Developer: 实现业务逻辑
- Tester: 编写测试用例" --claude
```

## 4. 方案二：ccswarm（高性能 Rust）

### 4.1 简介

ccswarm 使用 Rust 构建，特点：
- 零成本抽象
- Git worktree 隔离
- WebSocket 通信
- 通过 ACP（Agent Client Protocol）连接 Claude Code

### 4.2 安装

```bash
# 从源码构建
git clone https://github.com/nwiizo/ccswarm.git
cd ccswarm
cargo build --release

# 或直接安装
cargo install --path crates/ccswarm
```

### 4.3 多机器配置

**机器 A（主控）：**

```bash
# 初始化项目
ccswarm init --name "MyProject" --agents supervisor,developer,tester

# 启动编排器
ccswarm start

# 启动监控 UI
ccswarm tui
```

**机器 B（工作节点）：**

```bash
# 启动 Claude Code 并暴露 ACP
claude --acp-port 9100

# ccswarm 自动连接到 ws://machine-b:9100
```

### 4.4 配置文件

`ccswarm.toml`:

```toml
[project]
name = "multi-machine-dev"

[agents]
[agents.supervisor]
role = "supervisor"
machine = "ws://machine-a:9100"
capabilities = ["review", "test", "approve"]

[agents.developer]
role = "worker"
machine = "ws://machine-b:9100"
capabilities = ["code", "refactor"]

[agents.tester]
role = "worker"
machine = "ws://machine-c:9100"
capabilities = ["test", "report"]

[workflow]
pattern = "supervisor-worker"
```

## 5. 方案三：claude-code-by-agents（最简单）

### 5.1 简介

使用 @mentions 语法直接路由任务到指定代理，支持本地和远程混合。

### 5.2 安装

```bash
# 下载桌面应用或从源码运行
git clone https://github.com/baryhuang/claude-code-by-agents.git
cd claude-code-by-agents

# 启动后端
cd backend && deno task dev

# 启动前端
cd frontend && npm run dev
```

### 5.3 配置远程代理

在 Settings UI 中添加代理：

| 名称 | 端点 | 工作目录 |
|------|------|---------|
| supervisor | http://machine-a:8081 | /project |
| developer | http://machine-b:8081 | /project/src |
| tester | http://machine-c:8081 | /project/tests |

### 5.4 使用示例

```
# 直接指定代理
@supervisor 请审查 @developer 完成的代码

# 多代理协作
@supervisor 分解以下任务并分配给 @developer 和 @tester：
实现用户登录功能，包含单元测试
```

## 6. 方案四：自建简单协作系统

如果上述方案过于复杂，可以自建简单的协作系统。

### 6.1 架构设计

```
┌─────────────────┐     HTTP/WebSocket      ┌─────────────────┐
│   Machine A     │◄─────────────────────────►│   Machine B     │
│   (Supervisor)  │                          │   (Worker)      │
│                 │                          │                 │
│  ┌───────────┐  │                          │  ┌───────────┐  │
│  │ Claude    │  │     任务分配              │  │ Claude    │  │
│  │ Code      │  │─────────────────────────►│  │ Code      │  │
│  │           │  │                          │  │           │  │
│  │ - 任务分解 │  │     结果返回              │  │ - 代码实现 │  │
│  │ - 代码审查 │  │◄─────────────────────────│  │ - 测试执行 │  │
│  │ - 验收测试 │  │                          │  │           │  │
│  └───────────┘  │                          │  └───────────┘  │
│                 │                          │                 │
│  共享存储：      │                          │                 │
│  - Git 仓库     │◄─────── git push/pull ────►│                 │
│  - 任务队列     │                          │                 │
└─────────────────┘                          └─────────────────┘
```

### 6.2 基于 Git 的简单协作

**共享 Git 仓库作为通信媒介：**

```bash
# 任务文件结构
project/
├── .claude-tasks/
│   ├── pending/           # 待处理任务
│   │   └── task-001.md
│   ├── in-progress/       # 进行中
│   ├── review/            # 待审查
│   └── done/              # 已完成
├── src/
└── tests/
```

**Supervisor（机器 A）脚本：**

```bash
#!/bin/bash
# supervisor.sh - 监督者循环

while true; do
    # 拉取最新代码
    git pull

    # 检查是否有待审查的任务
    if ls .claude-tasks/review/*.md 1>/dev/null 2>&1; then
        for task in .claude-tasks/review/*.md; do
            # 让 Claude Code 审查
            claude -p "请审查以下任务的实现：$(cat $task)

            检查：
            1. 代码是否符合要求
            2. 测试是否通过
            3. 是否有安全问题

            如果通过，移动到 done/；否则写入反馈并移回 pending/"

            git add . && git commit -m "Review: $task" && git push
        done
    fi

    sleep 60
done
```

**Worker（机器 B）脚本：**

```bash
#!/bin/bash
# worker.sh - 工作者循环

while true; do
    git pull

    # 检查是否有待处理任务
    if ls .claude-tasks/pending/*.md 1>/dev/null 2>&1; then
        task=$(ls .claude-tasks/pending/*.md | head -1)

        # 移动到进行中
        mv "$task" .claude-tasks/in-progress/
        git add . && git commit -m "Start: $(basename $task)" && git push

        # 让 Claude Code 执行任务
        claude -p "请执行以下任务：$(cat .claude-tasks/in-progress/$(basename $task))

        完成后：
        1. 实现代码
        2. 编写测试
        3. 运行测试确保通过"

        # 移动到待审查
        mv ".claude-tasks/in-progress/$(basename $task)" .claude-tasks/review/
        git add . && git commit -m "Complete: $(basename $task)" && git push
    fi

    sleep 30
done
```

### 6.3 基于 MCP 的通信

创建简单的 MCP 服务器用于机器间通信：

**task-server.js（在 Supervisor 机器上运行）：**

```javascript
import express from 'express';
import { v4 as uuid } from 'uuid';

const app = express();
app.use(express.json());

const tasks = new Map();
const results = new Map();

// 创建任务
app.post('/tasks', (req, res) => {
    const id = uuid();
    tasks.set(id, {
        id,
        description: req.body.description,
        status: 'pending',
        assignee: req.body.assignee,
        created: new Date()
    });
    res.json({ id });
});

// 获取待处理任务
app.get('/tasks/pending', (req, res) => {
    const pending = [...tasks.values()].filter(t =>
        t.status === 'pending' && t.assignee === req.query.worker
    );
    res.json(pending);
});

// 提交任务结果
app.post('/tasks/:id/complete', (req, res) => {
    const task = tasks.get(req.params.id);
    if (task) {
        task.status = 'review';
        task.result = req.body.result;
        res.json({ success: true });
    } else {
        res.status(404).json({ error: 'Task not found' });
    }
});

// 审批任务
app.post('/tasks/:id/approve', (req, res) => {
    const task = tasks.get(req.params.id);
    if (task) {
        task.status = req.body.approved ? 'done' : 'pending';
        task.feedback = req.body.feedback;
        res.json({ success: true });
    }
});

app.listen(8080, () => console.log('Task server running on :8080'));
```

**配置 Claude Code 连接：**

```bash
# 在 Worker 机器上
claude mcp add --transport http task-server http://supervisor-machine:8080
```

## 7. Supervisor-Worker 模式最佳实践

### 7.1 角色定义

| 角色 | 职责 | 能力 |
|------|------|------|
| **Supervisor** | 任务分解、分配、审查、验收 | 项目管理、代码审查、测试验证 |
| **Developer** | 实现功能、修复 Bug | 编码、重构、文档 |
| **Tester** | 编写测试、执行测试、报告问题 | 单元测试、集成测试、性能测试 |

### 7.2 工作流程

```
1. Supervisor 收到需求
   ↓
2. Supervisor 分解任务，创建任务单
   ↓
3. Developer 领取任务，实现代码
   ↓
4. Developer 提交代码到 review
   ↓
5. Tester 编写并运行测试
   ↓
6. Tester 提交测试结果
   ↓
7. Supervisor 审查代码和测试
   ↓
8. 如果通过 → 完成
   如果失败 → 返回步骤 3，附带反馈
```

### 7.3 通信协议建议

使用结构化的任务描述：

```yaml
# task-001.yaml
id: task-001
title: 实现用户登录 API
description: |
  创建 POST /api/login 端点
  - 接收 username 和 password
  - 验证用户凭据
  - 返回 JWT token
priority: high
assignee: developer
dependencies: []
acceptance_criteria:
  - 单元测试覆盖率 > 80%
  - 通过安全审查
  - 响应时间 < 200ms
```

## 8. 内网部署注意事项

### 8.1 网络要求

| 通信路径 | 端口 | 协议 |
|---------|------|------|
| Supervisor ↔ Worker | 8080-9100 | HTTP/WebSocket |
| Claude Code → API | 443 | HTTPS |
| Git 同步 | 22/443 | SSH/HTTPS |

### 8.2 API 代理配置

如果内网无法直接访问 Anthropic API：

```bash
# 设置 API 代理
export ANTHROPIC_API_BASE_URL=https://your-proxy.internal/v1
export ANTHROPIC_API_KEY=your-key
```

### 8.3 离线场景

完全隔离的内网需要：
1. 私有部署的 LLM（如通过 Amazon Bedrock）
2. 或配置 API 网关代理

## 9. 成本估算

| 场景 | 预估成本 |
|------|---------|
| 10 个代理并行工作 | ~$2,000/月 |
| 单个复杂项目（50次迭代） | $50-100 |
| 企业团队（5人） | 可替代约 $50,000/月工程成本 |

## 10. 推荐选择

| 需求 | 推荐方案 |
|------|---------|
| 企业级、复杂项目 | **claude-flow** |
| 高性能、Rust 生态 | **ccswarm** |
| 简单快速上手 | **claude-code-by-agents** |
| Ruby 项目 | **SwarmSDK** |
| 完全自定义 | **自建系统** |

## 11. 相关资源

- [claude-flow](https://github.com/ruvnet/claude-flow) - 企业级多代理编排
- [ccswarm](https://github.com/nwiizo/ccswarm) - Rust 高性能编排
- [claude-code-by-agents](https://github.com/baryhuang/claude-code-by-agents) - @mentions 路由
- [SwarmSDK](https://github.com/parruda/swarm) - Ruby 框架
- [Multi-Agent Orchestration Guide](https://dev.to/bredmond1019/multi-agent-orchestration-running-10-claude-instances-in-parallel-part-3-29da)
- [3 Amigo Agents Pattern](https://medium.com/@george.vetticaden/the-3-amigo-agents-the-claude-code-development-pattern-i-discovered-while-implementing-anthropics-67b392ab4e3f)
- [Anthropic Cookbook - Orchestrator Workers](https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/orchestrator_workers.ipynb)

---

*本文档基于各开源项目文档整理*
