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

## 3. 安装方法

在 Claude Code 中运行：

```bash
/plugin install ralph-wiggum@claude-plugins-official
```

或者从官方仓库安装：
- [anthropics/claude-code/plugins/ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)

## 4. 命令使用

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

## 5. 提示编写最佳实践

### 5.1 明确的完成标准

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

### 5.2 增量目标

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

### 5.3 自我修正机制

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

### 5.4 安全逃生门

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

## 6. 设计哲学

Ralph 体现四个核心原则：

| 原则 | 说明 |
|------|------|
| **迭代 > 完美** | 不追求首次完美，让循环改进工作 |
| **失败即数据** | 可预测的失败是有价值的信息，用于调整提示 |
| **操作者技能重要** | 成功取决于写好提示，而非只依赖模型 |
| **持续就是胜利** | 继续尝试直到成功，循环自动处理重试逻辑 |

## 7. 适用场景

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

## 8. 实际成果

| 案例 | 成果 |
|------|------|
| Y Combinator 黑客马拉松 | 一夜之间生成 6 个仓库 |
| $50k 合同项目 | 仅花费 $297 API 成本完成 |
| CURSED 编程语言 | 3 个月循环创建了完整的编程语言 |

## 9. 成本考虑

自主循环会消耗大量 token：

- 在大型代码库上运行 50 次迭代可能花费 $50-100+ API 费用
- Claude Code 订阅用户会更快达到使用限制
- 建议始终设置 `--max-iterations` 限制

## 10. 相关资源

- [官方插件仓库](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)
- [Geoffrey Huntley 原始技术介绍](https://ghuntley.com/ralph/)
- [Ralph Orchestrator](https://github.com/mikeyobrien/ralph-orchestrator)
- [Awesome Claude - Ralph Wiggum](https://awesomeclaude.ai/ralph-wiggum)
- [Claude Plugin Hub](https://www.claudepluginhub.com/plugins/anthropics-ralph-wiggum-plugins-ralph-wiggum)

## 11. 快速开始示例

```bash
# 1. 安装插件
/plugin install ralph-wiggum@claude-plugins-official

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
