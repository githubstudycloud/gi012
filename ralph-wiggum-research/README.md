# Ralph Wiggum 插件研究指南

> 研究日期：2026-01-04

## 1. 概述

**Ralph Wiggum** 是 Claude Code 的一个自主循环插件，实现了迭代式、自我参照的 AI 开发循环技术。名字来源于《辛普森一家》中的角色 Ralph Wiggum，体现了"持续迭代直到成功"的哲学。

## 2. 核心概念

正如 Geoffrey Huntley 所描述的：**"Ralph is a Bash loop"** - 一个简单的 `while true` 循环，不断向 AI 代理输入提示文件，让它迭代改进工作直到完成。

```bash
while :; do cat PROMPT.md | claude ; done
```

### 工作原理

```
1. 你运行一次 /ralph-loop "任务描述"
2. Claude 开始工作
3. Claude 尝试退出
4. Stop hook 阻止退出
5. Stop hook 重新输入相同的提示
6. 重复直到完成
```

关键洞察：**提示永远不变**，但 Claude 之前的工作保留在文件中。每次迭代都能看到修改后的文件和 git 历史，所以 Claude 通过读取自己过去的工作来自主改进。

## 3. 插件安装来源

### 3.1 在线安装来源

插件从以下来源安装：

| 来源 | 地址 | 说明 |
|------|------|------|
| 官方插件仓库 | [anthropics/claude-code/plugins](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) | Claude Code 主仓库中的插件 |
| 官方插件集合 | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum) | Anthropic 维护的官方插件集 |
| 第三方实现 | [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code) | 增强版本，带监控功能 |

### 3.2 标准在线安装

```bash
# 方法 1：从官方 marketplace 安装
/plugin marketplace add anthropics/claude-code
/plugin install ralph-wiggum@claude-code-plugins

# 方法 2：直接从 GitHub 安装
/plugin install https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum
```

## 4. 内网离线安装方案

### 4.1 方案一：手动下载插件目录（推荐）

**步骤 1：在有网络的机器上下载插件**

```bash
# 克隆官方插件仓库
git clone https://github.com/anthropics/claude-plugins-official.git

# 或者只下载 ralph-wiggum 插件目录
# 访问 https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum
# 下载整个 ralph-wiggum 文件夹
```

**步骤 2：插件目录结构**

确保下载的目录结构如下：

```
ralph-wiggum/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── commands/
│   ├── ralph-loop.md        # /ralph-loop 命令
│   └── cancel-ralph.md      # /cancel-ralph 命令
├── hooks/
│   └── hooks.json           # Stop hook 配置
└── README.md
```

**步骤 3：复制到内网机器**

将整个 `ralph-wiggum` 目录复制到内网机器。

**步骤 4：本地安装**

```bash
# 方法 A：使用 --plugin-dir 标志加载
claude --plugin-dir /path/to/ralph-wiggum

# 方法 B：创建本地 marketplace
mkdir -p ~/local-plugins
cp -r ralph-wiggum ~/local-plugins/

# 在 Claude Code 中添加本地 marketplace
/plugin marketplace add ~/local-plugins
/plugin install ralph-wiggum@local-plugins

# 方法 C：直接放入项目目录
cp -r ralph-wiggum /your/project/.claude/plugins/
```

### 4.2 方案二：配置 settings.json

在项目的 `.claude/settings.json` 中直接配置：

```json
{
  "plugins": {
    "local": [
      {
        "path": "/absolute/path/to/ralph-wiggum",
        "enabled": true
      }
    ]
  }
}
```

或在用户级别配置 `~/.claude/settings.json`：

```json
{
  "plugins": {
    "directories": [
      "/path/to/local-plugins"
    ]
  }
}
```

### 4.3 方案三：第三方 Ralph 实现（frankbria/ralph-claude-code）

这个版本是独立的 bash 脚本，不依赖插件系统：

```bash
# 1. 在有网络的机器上下载
git clone https://github.com/frankbria/ralph-claude-code.git

# 2. 复制到内网机器

# 3. 安装（添加到 PATH）
cd ralph-claude-code
./install.sh

# 4. 使用
ralph-setup my-project
cd my-project
ralph --monitor
```

**特点：**
- 添加 `ralph`、`ralph-monitor`、`ralph-setup` 命令
- 内置速率限制（100 calls/hour）
- 熔断器防止失控循环
- tmux 监控面板

### 4.4 方案四：手动创建插件

如果无法获取官方插件，可以手动创建：

**1. 创建目录结构**

```bash
mkdir -p ralph-wiggum/.claude-plugin
mkdir -p ralph-wiggum/commands
mkdir -p ralph-wiggum/hooks
```

**2. 创建 plugin.json**

```json
{
  "name": "ralph-wiggum",
  "description": "Autonomous development loops for Claude Code",
  "version": "1.0.0",
  "author": {
    "name": "Local Installation"
  }
}
```

**3. 创建 commands/ralph-loop.md**

```markdown
# Ralph Loop

Start an autonomous development loop.

Usage: /ralph-loop "<prompt>" --max-iterations <n> --completion-promise "<text>"

This command starts a loop that:
1. Executes your prompt
2. Intercepts exit attempts
3. Re-feeds the prompt until completion or max iterations
```

**4. 创建 hooks/hooks.json**

```json
{
  "hooks": [
    {
      "type": "stop",
      "command": "check-ralph-completion",
      "description": "Intercept exits during Ralph loop"
    }
  ]
}
```

## 5. VSCode 扩展支持

### 5.1 支持情况

| 功能 | CLI | VSCode 扩展 |
|------|-----|-------------|
| 插件系统 | ✅ 完整支持 | ✅ 支持 |
| /ralph-loop 命令 | ✅ | ✅ |
| Stop hooks | ✅ | ✅ |
| 自主循环 | ✅ | ✅ |
| 监控面板 | ✅ (tmux) | ⚠️ 使用输出面板 |

### 5.2 在 VSCode 中使用

1. **确保已安装 Claude Code VSCode 扩展**
   - 在扩展市场搜索 "Claude Code"
   - 安装 Anthropic 官方扩展

2. **加载本地插件**

   在 VSCode 设置中配置：
   ```json
   {
     "claude-code.pluginDirectories": [
       "/path/to/local-plugins"
     ]
   }
   ```

3. **使用插件**

   在 Claude Code 面板中输入：
   ```
   /ralph-loop "Your task" --max-iterations 20
   ```

### 5.3 VSCode 中的限制

- VSCode 扩展中的 Ralph 循环可能受到 UI 刷新的影响
- 长时间运行的循环建议使用 CLI 版本
- 监控功能在 VSCode 中不如 CLI + tmux 直观

## 6. 命令使用

### `/ralph-loop` - 启动循环

```bash
/ralph-loop "<prompt>" --max-iterations <n> --completion-promise "<text>"
```

**参数：**
| 参数 | 说明 |
|------|------|
| `--max-iterations <n>` | N 次迭代后停止（默认：无限制） |
| `--completion-promise <text>` | 表示完成的信号短语 |

**示例：**
```bash
/ralph-loop "Build a REST API for todos. Requirements: CRUD operations, input validation, tests. Output <promise>COMPLETE</promise> when done." --completion-promise "COMPLETE" --max-iterations 50
```

### `/cancel-ralph` - 取消循环

```bash
/cancel-ralph
```

## 7. 提示编写最佳实践

### 7.1 明确的完成标准

**错误示例：**
```
Build a todo API and make it good.
```

**正确示例：**
```
Build a REST API for todos.

When complete:
- All CRUD endpoints working
- Input validation in place
- Tests passing (coverage > 80%)
- README with API docs
- Output: <promise>COMPLETE</promise>
```

### 7.2 增量目标

**错误示例：**
```
Create a complete e-commerce platform.
```

**正确示例：**
```
Phase 1: User authentication (JWT, tests)
Phase 2: Product catalog (list/search, tests)
Phase 3: Shopping cart (add/remove, tests)

Output <promise>COMPLETE</promise> when all phases done.
```

### 7.3 自我修正机制

**正确示例：**
```
Implement feature X following TDD:
1. Write failing tests
2. Implement feature
3. Run tests
4. If any fail, debug and fix
5. Refactor if needed
6. Repeat until all green
7. Output: <promise>COMPLETE</promise>
```

### 7.4 安全逃生门

始终使用 `--max-iterations` 作为安全网：

```bash
/ralph-loop "Try to implement feature X" --max-iterations 20
```

在提示中包含卡住时的处理方式：
```
After 15 iterations, if not complete:
- Document what's blocking progress
- List what was attempted
- Suggest alternative approaches
```

## 8. 设计哲学

Ralph 体现四个核心原则：

| 原则 | 说明 |
|------|------|
| **迭代 > 完美** | 不追求首次完美，让循环改进工作 |
| **失败即数据** | 可预测的失败是有价值的信息，用于调整提示 |
| **操作者技能重要** | 成功取决于写好提示，而非只依赖模型 |
| **持续就是胜利** | 继续尝试直到成功，循环自动处理重试逻辑 |

## 9. 适用场景

### 适合使用 Ralph 的场景

- 有明确成功标准的任务
- 需要迭代和改进的任务（如让测试通过）
- 可以放手让它运行的绿地项目
- 有自动验证机制的任务（测试、linter、构建）
- 文档生成
- 代码标准化
- 批量添加 TypeScript 类型

### 不适合使用 Ralph 的场景

- 需要人类判断或设计决策的任务
- 一次性操作
- 成功标准不明确的任务
- 生产环境调试
- 模糊的需求
- 架构决策（如微服务 vs 单体）
- 安全关键代码（认证、加密、支付处理）

## 10. 实际成果

| 案例 | 成果 |
|------|------|
| Y Combinator 黑客马拉松 | 一夜之间生成 6 个仓库 |
| $50k 合同项目 | 仅花费 $297 API 成本完成 |
| CURSED 编程语言 | 3 个月循环创建了完整的编程语言 |

## 11. 成本考虑

自主循环会消耗大量 token：

- 在大型代码库上运行 50 次迭代可能花费 $50-100+ API 费用
- Claude Code 订阅用户会更快达到使用限制
- 建议始终设置 `--max-iterations` 限制

## 12. 内网环境注意事项

### 12.1 API 访问

即使插件离线安装，**Claude Code 本身仍需要访问 Anthropic API**：

| 场景 | 解决方案 |
|------|---------|
| 完全隔离内网 | 需要配置代理或 API 网关 |
| 可访问外网 API | 只需离线安装插件即可 |
| 私有部署 | 使用 Amazon Bedrock 或 Google Vertex AI |

### 12.2 配置 API 代理

```bash
# 设置环境变量
export ANTHROPIC_API_BASE_URL=https://your-proxy.internal/v1
export ANTHROPIC_API_KEY=your-key
```

或在 `~/.claude.json` 中配置：

```json
{
  "apiBaseUrl": "https://your-proxy.internal/v1",
  "apiKey": "your-key"
}
```

## 13. 相关资源

- [官方插件仓库](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)
- [官方插件集合](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum)
- [第三方增强版](https://github.com/frankbria/ralph-claude-code)
- [Geoffrey Huntley 原始技术介绍](https://ghuntley.com/ralph/)
- [Ralph Orchestrator](https://github.com/mikeyobrien/ralph-orchestrator)
- [Awesome Claude - Ralph Wiggum](https://awesomeclaude.ai/ralph-wiggum)
- [Claude Plugin Hub](https://www.claudepluginhub.com/plugins/anthropics-ralph-wiggum-plugins-ralph-wiggum)
- [Claude Code 插件文档](https://code.claude.com/docs/en/plugins)

## 14. 快速开始示例

```bash
# 1. 安装插件（在线）
/plugin install ralph-wiggum@claude-plugins-official

# 1. 或离线安装
claude --plugin-dir /path/to/ralph-wiggum

# 2. 启动循环
/ralph-loop "Create a CLI tool that converts markdown to HTML.
Requirements:
- Support basic markdown syntax
- Handle code blocks with syntax highlighting
- Include unit tests
- Create README with usage examples

Output <promise>DONE</promise> when all requirements met." --completion-promise "DONE" --max-iterations 30

# 3. 如需取消
/cancel-ralph
```

---

*本文档基于官方文档和 Geoffrey Huntley 的博客整理*

**参考来源：**
- https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
- https://github.com/anthropics/claude-plugins-official
- https://github.com/frankbria/ralph-claude-code
- https://ghuntley.com/ralph/
- https://code.claude.com/docs/en/plugins
