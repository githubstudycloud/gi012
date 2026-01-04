# AI Service Hub - 简化版多 AI 服务管理中心

> 一个简单易用的多 AI 服务编排工具，带 Web 图形界面

## 概述

```
┌────────────────────────────────────────────────────────────┐
│                    Web 管理界面 (localhost:8080)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 服务管理  │ │ 任务分配  │ │ Token统计│ │ 日志查看  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         ┌────────┐   ┌────────┐   ┌────────┐
         │ Codex  │   │ Gemini │   │ Claude │
         │ #001   │   │ #002   │   │ #003   │
         └────────┘   └────────┘   └────────┘
```

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <repo-url>
cd ai-service-hub

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

### 2. 打开管理界面

浏览器访问：http://localhost:8080

### 3. 添加 AI 服务

在 Web 界面点击「添加服务」，填写：
- 服务名称
- 类型（Codex/Gemini/Claude）
- 连接方式（SSH/Docker/本地）
- 主机地址

## 目录结构

```
ai-service-hub/
├── app.py              # 主程序入口
├── config.json         # 配置文件（自动生成）
├── requirements.txt    # 依赖
├── static/             # 前端静态文件
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

## 功能说明

### 服务管理
- 添加/删除/编辑 AI 服务
- 一键测试连接
- 实时状态监控

### 任务分配
- 手动指定服务执行任务
- 自动路由（按服务能力）
- 并行执行对比结果

### Token 统计
- 各服务使用量统计
- 每日/每周报表
- 预算预警

## 配置文件说明

`config.json` 示例：

```json
{
  "services": [
    {
      "id": "001",
      "name": "Codex-Mac",
      "type": "codex",
      "host": "mac-mini.local",
      "port": 22,
      "protocol": "ssh",
      "enabled": true
    }
  ],
  "token_budget": {
    "daily_limit": 100000
  }
}
```
