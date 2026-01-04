# Claude Code 插件研究指南

> 研究日期：2026-01-04

## 1. 概述

Claude Code 是 Anthropic 官方的 CLI 工具，也有 VS Code 扩展版本。它是一个 AI 驱动的编程助手，可以帮助开发者完成软件工程任务。

## 2. 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 10.15+、Ubuntu 20.04+/Debian 10+、Windows 10+（WSL/Git Bash） |
| 内存 | 4GB+ RAM |
| Node.js | 18+（仅 NPM 安装需要） |
| 网络 | 需要互联网连接 |
| Shell | Bash、Zsh 或 Fish |

## 3. 安装方法

### 方法 A：原生安装（推荐）

**macOS/Linux/WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**
```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

### 方法 B：Homebrew
```bash
brew install --cask claude-code
```

### 方法 C：NPM
```bash
npm install -g @anthropic-ai/claude-code
```

### 验证安装
```bash
claude doctor
```

## 4. VS Code 扩展安装

1. 打开 VS Code
2. 按 `Ctrl+Shift+X`（Windows/Linux）或 `Cmd+Shift+X`（Mac）
3. 搜索 "Claude Code"
4. 点击 **Install**

### 扩展设置

| 设置项 | 说明 | 默认值 |
|--------|------|-------|
| Selected Model | 默认模型 | Opus |
| Use Terminal | 使用终端模式 | false |
| Initial Permission Mode | 默认权限模式 | default |
| Autosave | 自动保存文件 | true |

## 5. 认证方式

启动 Claude Code：
```bash
cd /path/to/your/project
claude
```

支持三种认证方式：
1. **Claude Console** - 需要在 Anthropic console 激活计费
2. **Claude App** - Pro/Max 订阅用户
3. **企业平台** - Amazon Bedrock、Google Vertex AI、Microsoft Foundry

## 6. 主要功能

### 文件和代码操作
- **Read** - 读取文件内容
- **Write** - 创建或覆写文件
- **Edit** - 对文件进行编辑
- **Glob** - 基于模式查找文件
- **Grep** - 搜索文件内容

### 开发工具
- **Bash** - 执行 shell 命令
- **Task** - 运行子代理处理复杂任务
- **WebFetch** - 从 URL 获取内容
- **WebSearch** - 执行 Web 搜索
- **TodoWrite** - 创建和管理任务列表

## 7. 常用命令

### 启动命令

| 命令 | 用途 |
|------|------|
| `claude` | 启动交互模式 |
| `claude "任务"` | 执行一次性任务 |
| `claude -p "query"` | 一次性查询后退出 |
| `claude -c` | 继续最近的对话 |
| `claude commit` | 创建 Git 提交 |

### 内部命令（以 `/` 开头）

```
/help              显示可用命令
/login             登录账号
/logout            退出登录
/config            打开设置界面
/memory            管理 CLAUDE.md 文件
/mcp               配置 MCP 服务器
/resume            恢复之前的对话
/model             查看或切换模型
/clear             清除对话历史
/tree              显示项目结构
```

## 8. 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+C` | 取消输入或生成 |
| `Ctrl+D` | 退出会话 |
| `Ctrl+L` | 清空屏幕 |
| `Ctrl+O` | 切换详细输出 |
| `Ctrl+R` | 反向搜索历史 |
| `↑/↓` | 导航历史 |
| `Esc+Esc` | 回退代码/对话 |
| `Shift+Tab` | 切换权限模式 |

## 9. MCP 服务器配置

MCP（Model Context Protocol）用于连接外部工具、数据库和 API。

### 安装 MCP 服务器

```bash
# HTTP 服务器
claude mcp add --transport http <name> <url>

# SSE 服务器
claude mcp add --transport sse <name> <url>

# 本地 Stdio 服务器
claude mcp add --transport stdio <name> -- <command>
```

### 管理命令

```bash
claude mcp list        # 列出所有服务器
claude mcp get <name>  # 获取详情
claude mcp remove <name>  # 删除服务器
```

## 10. 项目配置

### CLAUDE.md 文件

在项目根目录创建 `CLAUDE.md` 来提供项目上下文：

```markdown
# Project Name

## Project Overview
- 主要功能描述
- 技术栈

## Key Files
- `src/main.ts` - 入口点

## Important Notes
- 特殊约定
```

### 权限配置

在 `.claude/settings.json` 中配置：

```json
{
  "permissions": {
    "allow": ["Bash(npm run test:*)"],
    "deny": ["Read(.env)"]
  }
}
```

## 11. 关键文件和目录

| 位置 | 用途 |
|------|------|
| `~/.claude/settings.json` | 全局用户设置 |
| `~/.claude.json` | 认证令牌和 MCP 配置 |
| `.claude/settings.json` | 项目级共享设置 |
| `.claude/commands/` | 项目级自定义命令 |
| `.mcp.json` | 项目级 MCP 服务器配置 |
| `CLAUDE.md` | 项目上下文和指令 |

## 12. 更新和卸载

### 更新
```bash
claude update
```

### 卸载

**原生安装：**
```bash
# macOS/Linux/WSL
rm -f ~/.local/bin/claude
rm -rf ~/.claude-code

# Windows PowerShell
Remove-Item -Path "$env:LOCALAPPDATA\Programs\claude-code" -Recurse -Force
```

**Homebrew：**
```bash
brew uninstall --cask claude-code
```

**NPM：**
```bash
npm uninstall -g @anthropic-ai/claude-code
```

## 13. 最佳实践

1. **使用 CLAUDE.md** - 为项目提供上下文信息
2. **配置权限** - 限制敏感文件的访问
3. **使用 Plan Mode** - 复杂任务前先规划
4. **命名会话** - 使用 `/rename` 便于后续查找
5. **自定义命令** - 在 `.claude/commands/` 创建常用操作

## 14. 故障排除

| 问题 | 解决方案 |
|------|---------|
| VS Code 扩展无法安装 | 确保 VS Code 1.98.0+ |
| CLI 命令找不到 | 检查 PATH 设置，重启 shell |
| MCP 连接失败 | 检查 URL 和认证凭据 |

---

*本文档基于 Claude Code 官方文档整理*
