# 多 AI 服务编排器设计方案

> 研究日期：2026-01-04
> 参考项目：[GuDaStudio/skills](https://github.com/GuDaStudio/skills)

## 1. 项目目标

构建一个以本地 Claude Code 为主控的多 AI 服务编排系统：

- **主控**：本地 Claude Code
- **被控服务**：远程/本地 Linux、Docker、Mac 上的 Codex、Gemini、Claude Code
- **特性**：
  - 动态接入多个服务（有多少接多少）
  - Git 管理每个服务的工具和配置
  - 配置与代码隔离
  - Skill 管理控制 token 消耗
  - 服务编号管理

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    本地 Claude Code（主控）                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Skill Manager                             │   │
│  │  - 加载/卸载 Skills                                          │   │
│  │  - Token 预算控制                                            │   │
│  │  - 服务路由决策                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌───────────────────────────┼───────────────────────────────┐     │
│  │                    Service Registry                        │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │     │
│  │  │ S001    │ │ S002    │ │ S003    │ │ S00N    │         │     │
│  │  │ Codex   │ │ Gemini  │ │ Claude  │ │ ...     │         │     │
│  │  │ @mac-1  │ │ @linux-1│ │ @docker │ │         │         │     │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘         │     │
│  └───────┼───────────┼───────────┼───────────┼───────────────┘     │
└──────────┼───────────┼───────────┼───────────┼──────────────────────┘
           │           │           │           │
           ▼           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Mac Mini │ │ Linux VM │ │ Docker   │ │ Cloud    │
    │ Codex CLI│ │ Gemini   │ │ Claude   │ │ Server   │
    │          │ │ CLI      │ │ Code     │ │          │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

## 3. 目录结构设计

```
multi-ai-orchestrator/
├── config/                          # 配置目录（Git 管理）
│   ├── services/                    # 服务配置
│   │   ├── S001-codex-mac.yaml
│   │   ├── S002-gemini-linux.yaml
│   │   ├── S003-claude-docker.yaml
│   │   └── ...
│   ├── routing/                     # 路由规则
│   │   ├── task-routing.yaml
│   │   └── fallback.yaml
│   ├── token-budget/                # Token 预算
│   │   ├── daily-limits.yaml
│   │   └── per-service-limits.yaml
│   └── global.yaml                  # 全局配置
│
├── skills/                          # Skills 目录（Git submodules）
│   ├── service-s001-codex/          # 服务 S001 的 Skill
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── bridge.py
│   │   └── templates/
│   ├── service-s002-gemini/
│   ├── service-s003-claude/
│   └── orchestrator/                # 编排器核心 Skill
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── router.py
│       │   ├── token_manager.py
│       │   └── service_registry.py
│       └── hooks/
│
├── code/                            # 代码目录（Git 管理，与配置隔离）
│   ├── bridges/                     # 各服务桥接代码
│   │   ├── codex_bridge.py
│   │   ├── gemini_bridge.py
│   │   └── claude_bridge.py
│   ├── core/                        # 核心库
│   │   ├── service_manager.py
│   │   ├── token_tracker.py
│   │   └── git_ops.py
│   └── utils/
│
├── .claude/                         # Claude Code 配置
│   ├── settings.json
│   └── CLAUDE.md
│
├── .git/                            # 主仓库
├── .gitmodules                      # Submodules 配置
└── README.md
```

## 4. 服务配置设计

### 4.1 服务配置文件格式

`config/services/S001-codex-mac.yaml`:

```yaml
# 服务基本信息
service:
  id: S001
  name: codex-mac-mini
  type: codex
  version: "1.0.0"
  enabled: true

# 连接配置
connection:
  host: mac-mini.local
  port: 22
  protocol: ssh  # ssh | http | websocket | docker
  auth:
    type: ssh-key
    key_path: ~/.ssh/id_rsa
    user: developer

# 服务能力
capabilities:
  - code_generation
  - debugging
  - algorithm_design
  - code_review

# 专长领域（用于路由决策）
specialties:
  languages:
    - python
    - javascript
    - typescript
  domains:
    - backend
    - algorithms
    - data_processing

# 安全设置
security:
  sandbox: read-only  # read-only | workspace-write | full-access
  allowed_paths:
    - /workspace
    - /tmp
  forbidden_commands:
    - rm -rf
    - sudo

# Token 预算
token_budget:
  daily_limit: 100000
  per_request_limit: 10000
  priority: high  # low | medium | high | critical

# 健康检查
health_check:
  enabled: true
  interval: 60  # seconds
  timeout: 10
  retry: 3
```

### 4.2 全局配置

`config/global.yaml`:

```yaml
orchestrator:
  name: multi-ai-orchestrator
  version: "1.0.0"

# 服务发现
discovery:
  auto_register: true
  scan_interval: 300  # seconds
  config_path: ./config/services/

# Token 管理
token_management:
  global_daily_limit: 500000
  warning_threshold: 0.8
  emergency_reserve: 10000
  tracking_enabled: true
  log_path: ./logs/token_usage/

# 路由策略
routing:
  default_strategy: capability_match  # round_robin | capability_match | cost_optimize | latency_optimize
  fallback_enabled: true
  retry_count: 3
  timeout: 30

# Git 集成
git:
  auto_commit: true
  config_branch: config
  code_branch: main
  sync_interval: 300

# 日志
logging:
  level: INFO
  format: json
  output:
    - console
    - file: ./logs/orchestrator.log
```

### 4.3 路由规则配置

`config/routing/task-routing.yaml`:

```yaml
# 任务类型路由规则
rules:
  - name: python_backend
    condition:
      task_type: code_generation
      language: python
      domain: backend
    route_to:
      - S001  # Codex
      - S003  # Claude
    strategy: capability_match

  - name: frontend_ui
    condition:
      task_type: code_generation
      language:
        - javascript
        - typescript
      domain: frontend
    route_to:
      - S002  # Gemini
    strategy: direct

  - name: code_review
    condition:
      task_type: review
    route_to:
      - S003  # Claude (supervisor)
    strategy: direct

  - name: algorithm
    condition:
      task_type: algorithm
    route_to:
      - S001  # Codex
      - S002  # Gemini
    strategy: parallel_compare

# 默认路由
default:
  route_to:
    - S001
    - S002
    - S003
  strategy: round_robin
```

## 5. Skill 实现

### 5.1 编排器核心 Skill

`skills/orchestrator/SKILL.md`:

```markdown
# Multi-AI Orchestrator Skill

## Description
This skill manages multiple AI services, routes tasks based on capabilities,
and controls token consumption across all connected services.

## Capabilities
- Service registration and discovery
- Task routing based on capabilities
- Token budget management
- Health monitoring
- Result aggregation

## Commands

### Register Service
```bash
python scripts/service_registry.py register --config <path>
```

### Route Task
```bash
python scripts/router.py --task "<task>" --type <type> --lang <language>
```

### Check Token Budget
```bash
python scripts/token_manager.py status
```

### List Services
```bash
python scripts/service_registry.py list
```

## Usage Examples

### Route a coding task
When you need to delegate a coding task, use:
```
@orchestrator route --task "Implement user authentication" --type code_generation --lang python
```

### Check service health
```
@orchestrator health --all
```

### Get token usage report
```
@orchestrator tokens --report daily
```
```

### 5.2 服务桥接 Skill 模板

`skills/service-s001-codex/SKILL.md`:

```markdown
# Service S001 - Codex Bridge

## Description
Bridge to OpenAI Codex CLI running on mac-mini.local

## Service Info
- **ID**: S001
- **Type**: Codex
- **Host**: mac-mini.local
- **Status**: Active

## Capabilities
- Python code generation
- Algorithm implementation
- Debugging assistance
- Code optimization

## Commands

### Execute Task
```bash
python scripts/bridge.py \
  --PROMPT "<task>" \
  --cd "<working_dir>" \
  --sandbox read-only \
  --SESSION_ID "<session_id>"
```

### Check Health
```bash
python scripts/bridge.py --health-check
```

## Token Budget
- Daily Limit: 100,000 tokens
- Per Request: 10,000 tokens
- Current Usage: {dynamic}

## Security
- Sandbox Mode: read-only
- Output: unified diff patches only
- No direct filesystem writes
```

## 6. 核心代码实现

### 6.1 服务管理器

`code/core/service_manager.py`:

```python
#!/usr/bin/env python3
"""
Multi-AI Service Manager
管理多个 AI 服务的注册、发现、健康检查
"""

import yaml
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import asyncio
import aiohttp


class ServiceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ConnectionProtocol(Enum):
    SSH = "ssh"
    HTTP = "http"
    WEBSOCKET = "websocket"
    DOCKER = "docker"
    LOCAL = "local"


@dataclass
class ServiceConfig:
    id: str
    name: str
    service_type: str
    host: str
    port: int
    protocol: ConnectionProtocol
    capabilities: List[str]
    specialties: Dict
    token_budget: Dict
    enabled: bool = True
    status: ServiceStatus = ServiceStatus.UNKNOWN


@dataclass
class ServiceRegistry:
    services: Dict[str, ServiceConfig] = field(default_factory=dict)
    config_path: Path = Path("./config/services")

    def load_all_services(self):
        """加载所有服务配置"""
        for config_file in self.config_path.glob("*.yaml"):
            self.load_service(config_file)

    def load_service(self, config_file: Path):
        """加载单个服务配置"""
        with open(config_file) as f:
            config = yaml.safe_load(f)

        service = ServiceConfig(
            id=config['service']['id'],
            name=config['service']['name'],
            service_type=config['service']['type'],
            host=config['connection']['host'],
            port=config['connection']['port'],
            protocol=ConnectionProtocol(config['connection']['protocol']),
            capabilities=config['capabilities'],
            specialties=config['specialties'],
            token_budget=config['token_budget'],
            enabled=config['service']['enabled']
        )

        self.services[service.id] = service
        print(f"Loaded service: {service.id} - {service.name}")

    def register_service(self, config: dict) -> str:
        """动态注册新服务"""
        service_id = config['service']['id']
        config_file = self.config_path / f"{service_id}-{config['service']['name']}.yaml"

        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        self.load_service(config_file)
        return service_id

    def unregister_service(self, service_id: str):
        """注销服务"""
        if service_id in self.services:
            del self.services[service_id]
            # 可选：移动配置文件到 archived/

    def get_service(self, service_id: str) -> Optional[ServiceConfig]:
        """获取服务配置"""
        return self.services.get(service_id)

    def list_services(self, filter_type: str = None) -> List[ServiceConfig]:
        """列出服务"""
        services = list(self.services.values())
        if filter_type:
            services = [s for s in services if s.service_type == filter_type]
        return services

    async def check_health(self, service_id: str) -> ServiceStatus:
        """检查服务健康状态"""
        service = self.get_service(service_id)
        if not service:
            return ServiceStatus.UNKNOWN

        try:
            if service.protocol == ConnectionProtocol.SSH:
                return await self._check_ssh_health(service)
            elif service.protocol == ConnectionProtocol.HTTP:
                return await self._check_http_health(service)
            elif service.protocol == ConnectionProtocol.DOCKER:
                return await self._check_docker_health(service)
            else:
                return ServiceStatus.UNKNOWN
        except Exception as e:
            print(f"Health check failed for {service_id}: {e}")
            return ServiceStatus.OFFLINE

    async def _check_ssh_health(self, service: ServiceConfig) -> ServiceStatus:
        """SSH 健康检查"""
        cmd = f"ssh -o ConnectTimeout=5 {service.host} 'echo ok'"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return ServiceStatus.ONLINE if b'ok' in stdout else ServiceStatus.OFFLINE

    async def _check_http_health(self, service: ServiceConfig) -> ServiceStatus:
        """HTTP 健康检查"""
        async with aiohttp.ClientSession() as session:
            url = f"http://{service.host}:{service.port}/health"
            async with session.get(url, timeout=5) as resp:
                return ServiceStatus.ONLINE if resp.status == 200 else ServiceStatus.DEGRADED

    async def _check_docker_health(self, service: ServiceConfig) -> ServiceStatus:
        """Docker 健康检查"""
        cmd = f"docker inspect --format='{{{{.State.Health.Status}}}}' {service.name}"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        status = stdout.decode().strip()
        return ServiceStatus.ONLINE if status == 'healthy' else ServiceStatus.DEGRADED

    async def check_all_health(self) -> Dict[str, ServiceStatus]:
        """检查所有服务健康状态"""
        results = {}
        tasks = [self.check_health(sid) for sid in self.services]
        statuses = await asyncio.gather(*tasks)
        for sid, status in zip(self.services.keys(), statuses):
            results[sid] = status
            self.services[sid].status = status
        return results


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Service Manager")
    parser.add_argument("command", choices=["list", "register", "health", "unregister"])
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--id", help="Service ID")
    parser.add_argument("--type", help="Filter by service type")

    args = parser.parse_args()

    registry = ServiceRegistry()
    registry.load_all_services()

    if args.command == "list":
        services = registry.list_services(args.type)
        for s in services:
            print(f"{s.id}: {s.name} ({s.service_type}) - {s.status.value}")

    elif args.command == "register":
        if args.config:
            with open(args.config) as f:
                config = yaml.safe_load(f)
            sid = registry.register_service(config)
            print(f"Registered: {sid}")

    elif args.command == "health":
        results = asyncio.run(registry.check_all_health())
        for sid, status in results.items():
            print(f"{sid}: {status.value}")

    elif args.command == "unregister":
        if args.id:
            registry.unregister_service(args.id)
            print(f"Unregistered: {args.id}")
```

### 6.2 Token 管理器

`code/core/token_tracker.py`:

```python
#!/usr/bin/env python3
"""
Token Budget Manager
管理所有服务的 Token 预算和使用情况
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Dict, Optional
import sqlite3


@dataclass
class TokenUsage:
    service_id: str
    date: date
    used: int = 0
    limit: int = 0
    requests: int = 0


class TokenTracker:
    def __init__(self, db_path: str = "./data/tokens.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_budgets()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                date TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                requests INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service_id, date)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS token_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                tokens INTEGER NOT NULL,
                task_type TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _load_budgets(self):
        """加载预算配置"""
        self.budgets = {}
        budget_file = Path("./config/token-budget/per-service-limits.yaml")
        if budget_file.exists():
            with open(budget_file) as f:
                self.budgets = yaml.safe_load(f)

    def get_daily_limit(self, service_id: str) -> int:
        """获取服务的日预算"""
        return self.budgets.get(service_id, {}).get('daily_limit', 100000)

    def get_usage(self, service_id: str, target_date: date = None) -> TokenUsage:
        """获取服务的 Token 使用情况"""
        if target_date is None:
            target_date = date.today()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT tokens_used, requests FROM token_usage WHERE service_id = ? AND date = ?",
            (service_id, target_date.isoformat())
        )
        row = cursor.fetchone()
        conn.close()

        return TokenUsage(
            service_id=service_id,
            date=target_date,
            used=row[0] if row else 0,
            limit=self.get_daily_limit(service_id),
            requests=row[1] if row else 0
        )

    def record_usage(self, service_id: str, tokens: int, task_type: str = None, session_id: str = None):
        """记录 Token 使用"""
        today = date.today().isoformat()

        conn = sqlite3.connect(self.db_path)

        # 更新日统计
        conn.execute("""
            INSERT INTO token_usage (service_id, date, tokens_used, requests)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(service_id, date) DO UPDATE SET
                tokens_used = tokens_used + ?,
                requests = requests + 1
        """, (service_id, today, tokens, tokens))

        # 记录详细日志
        conn.execute("""
            INSERT INTO token_log (service_id, tokens, task_type, session_id)
            VALUES (?, ?, ?, ?)
        """, (service_id, tokens, task_type, session_id))

        conn.commit()
        conn.close()

    def check_budget(self, service_id: str, required_tokens: int) -> tuple[bool, str]:
        """检查是否有足够预算"""
        usage = self.get_usage(service_id)
        remaining = usage.limit - usage.used

        if remaining >= required_tokens:
            return True, f"OK: {remaining} tokens remaining"
        else:
            return False, f"EXCEEDED: need {required_tokens}, only {remaining} remaining"

    def get_all_usage(self, target_date: date = None) -> Dict[str, TokenUsage]:
        """获取所有服务的使用情况"""
        if target_date is None:
            target_date = date.today()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT service_id, tokens_used, requests FROM token_usage WHERE date = ?",
            (target_date.isoformat(),)
        )

        results = {}
        for row in cursor.fetchall():
            results[row[0]] = TokenUsage(
                service_id=row[0],
                date=target_date,
                used=row[1],
                limit=self.get_daily_limit(row[0]),
                requests=row[2]
            )

        conn.close()
        return results

    def get_report(self, days: int = 7) -> dict:
        """生成使用报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT service_id, SUM(tokens_used), SUM(requests), COUNT(DISTINCT date)
            FROM token_usage
            WHERE date >= date('now', ?)
            GROUP BY service_id
        """, (f'-{days} days',))

        report = {
            'period_days': days,
            'services': {}
        }

        for row in cursor.fetchall():
            report['services'][row[0]] = {
                'total_tokens': row[1],
                'total_requests': row[2],
                'active_days': row[3],
                'avg_daily': row[1] // row[3] if row[3] > 0 else 0
            }

        conn.close()
        return report


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Token Tracker")
    parser.add_argument("command", choices=["status", "report", "check", "record"])
    parser.add_argument("--service", "-s", help="Service ID")
    parser.add_argument("--tokens", "-t", type=int, help="Token count")
    parser.add_argument("--days", "-d", type=int, default=7, help="Report days")

    args = parser.parse_args()

    tracker = TokenTracker()

    if args.command == "status":
        if args.service:
            usage = tracker.get_usage(args.service)
            pct = (usage.used / usage.limit * 100) if usage.limit > 0 else 0
            print(f"{usage.service_id}: {usage.used:,}/{usage.limit:,} ({pct:.1f}%)")
        else:
            all_usage = tracker.get_all_usage()
            for sid, usage in all_usage.items():
                pct = (usage.used / usage.limit * 100) if usage.limit > 0 else 0
                print(f"{sid}: {usage.used:,}/{usage.limit:,} ({pct:.1f}%)")

    elif args.command == "report":
        report = tracker.get_report(args.days)
        print(json.dumps(report, indent=2))

    elif args.command == "check":
        if args.service and args.tokens:
            ok, msg = tracker.check_budget(args.service, args.tokens)
            print(f"{'✓' if ok else '✗'} {msg}")

    elif args.command == "record":
        if args.service and args.tokens:
            tracker.record_usage(args.service, args.tokens)
            print(f"Recorded {args.tokens} tokens for {args.service}")
```

### 6.3 任务路由器

`code/core/router.py`:

```python
#!/usr/bin/env python3
"""
Task Router
根据任务类型和服务能力路由到最合适的服务
"""

import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class RoutingStrategy(Enum):
    DIRECT = "direct"
    ROUND_ROBIN = "round_robin"
    CAPABILITY_MATCH = "capability_match"
    COST_OPTIMIZE = "cost_optimize"
    LATENCY_OPTIMIZE = "latency_optimize"
    PARALLEL_COMPARE = "parallel_compare"


@dataclass
class TaskRequest:
    task: str
    task_type: str
    language: str = None
    domain: str = None
    priority: str = "medium"
    max_tokens: int = 10000


@dataclass
class RoutingDecision:
    target_services: List[str]
    strategy: RoutingStrategy
    reason: str
    estimated_tokens: int


class TaskRouter:
    def __init__(self, config_path: str = "./config/routing"):
        self.config_path = Path(config_path)
        self._load_rules()
        self._load_services()

    def _load_rules(self):
        """加载路由规则"""
        rules_file = self.config_path / "task-routing.yaml"
        if rules_file.exists():
            with open(rules_file) as f:
                config = yaml.safe_load(f)
                self.rules = config.get('rules', [])
                self.default_rule = config.get('default', {})

    def _load_services(self):
        """加载服务信息"""
        from service_manager import ServiceRegistry
        self.registry = ServiceRegistry()
        self.registry.load_all_services()

    def route(self, request: TaskRequest) -> RoutingDecision:
        """路由任务到合适的服务"""

        # 1. 尝试匹配规则
        for rule in self.rules:
            if self._match_rule(request, rule):
                return RoutingDecision(
                    target_services=rule['route_to'],
                    strategy=RoutingStrategy(rule['strategy']),
                    reason=f"Matched rule: {rule['name']}",
                    estimated_tokens=self._estimate_tokens(request)
                )

        # 2. 基于能力匹配
        matched = self._capability_match(request)
        if matched:
            return RoutingDecision(
                target_services=matched,
                strategy=RoutingStrategy.CAPABILITY_MATCH,
                reason="Matched by capabilities",
                estimated_tokens=self._estimate_tokens(request)
            )

        # 3. 使用默认规则
        return RoutingDecision(
            target_services=self.default_rule.get('route_to', []),
            strategy=RoutingStrategy(self.default_rule.get('strategy', 'round_robin')),
            reason="Using default routing",
            estimated_tokens=self._estimate_tokens(request)
        )

    def _match_rule(self, request: TaskRequest, rule: dict) -> bool:
        """检查请求是否匹配规则"""
        condition = rule.get('condition', {})

        # 匹配任务类型
        if 'task_type' in condition:
            if request.task_type != condition['task_type']:
                return False

        # 匹配语言
        if 'language' in condition:
            lang_cond = condition['language']
            if isinstance(lang_cond, list):
                if request.language not in lang_cond:
                    return False
            elif request.language != lang_cond:
                return False

        # 匹配领域
        if 'domain' in condition:
            if request.domain != condition['domain']:
                return False

        return True

    def _capability_match(self, request: TaskRequest) -> List[str]:
        """基于能力匹配服务"""
        matched = []

        for sid, service in self.registry.services.items():
            if not service.enabled:
                continue

            # 检查语言支持
            if request.language:
                if request.language in service.specialties.get('languages', []):
                    matched.append(sid)
                    continue

            # 检查领域支持
            if request.domain:
                if request.domain in service.specialties.get('domains', []):
                    matched.append(sid)
                    continue

            # 检查任务类型能力
            if request.task_type in service.capabilities:
                matched.append(sid)

        return matched

    def _estimate_tokens(self, request: TaskRequest) -> int:
        """估算任务所需 Token"""
        # 简单估算：任务描述长度 * 系数 + 基础消耗
        base_tokens = 1000
        task_length_factor = len(request.task) * 2
        complexity_factor = {
            'code_generation': 3,
            'review': 2,
            'debug': 2.5,
            'algorithm': 4,
            'refactor': 2
        }.get(request.task_type, 2)

        return int(base_tokens + task_length_factor * complexity_factor)

    def get_service_load(self) -> Dict[str, float]:
        """获取各服务负载（用于负载均衡）"""
        from token_tracker import TokenTracker
        tracker = TokenTracker()

        loads = {}
        for sid in self.registry.services:
            usage = tracker.get_usage(sid)
            if usage.limit > 0:
                loads[sid] = usage.used / usage.limit
            else:
                loads[sid] = 0.0

        return loads


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Task Router")
    parser.add_argument("--task", "-t", required=True, help="Task description")
    parser.add_argument("--type", required=True, help="Task type")
    parser.add_argument("--lang", help="Programming language")
    parser.add_argument("--domain", help="Domain (backend/frontend/etc)")

    args = parser.parse_args()

    router = TaskRouter()
    request = TaskRequest(
        task=args.task,
        task_type=args.type,
        language=args.lang,
        domain=args.domain
    )

    decision = router.route(request)

    print(f"Target Services: {', '.join(decision.target_services)}")
    print(f"Strategy: {decision.strategy.value}")
    print(f"Reason: {decision.reason}")
    print(f"Estimated Tokens: {decision.estimated_tokens:,}")
```

## 7. 服务桥接实现

### 7.1 通用桥接基类

`code/bridges/base_bridge.py`:

```python
#!/usr/bin/env python3
"""
Base Bridge Class
所有服务桥接的基类
"""

import json
import subprocess
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class BridgeResponse:
    success: bool
    session_id: str
    message: str
    tokens_used: int = 0
    output: Any = None
    error: str = None


class BaseBridge(ABC):
    """服务桥接基类"""

    def __init__(self, service_id: str, config: dict):
        self.service_id = service_id
        self.config = config
        self.host = config['connection']['host']
        self.port = config['connection']['port']
        self.protocol = config['connection']['protocol']

    @abstractmethod
    async def execute(self, prompt: str, working_dir: str,
                      session_id: str = None, **kwargs) -> BridgeResponse:
        """执行任务"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

    async def _run_ssh_command(self, command: str) -> tuple[int, str, str]:
        """执行 SSH 命令"""
        ssh_cmd = f"ssh {self.host} '{command}'"
        proc = await asyncio.create_subprocess_shell(
            ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode(), stderr.decode()

    async def _run_docker_command(self, command: str, container: str) -> tuple[int, str, str]:
        """执行 Docker 命令"""
        docker_cmd = f"docker exec {container} {command}"
        proc = await asyncio.create_subprocess_shell(
            docker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode(), stderr.decode()
```

### 7.2 Codex 桥接

`code/bridges/codex_bridge.py`:

```python
#!/usr/bin/env python3
"""
Codex Bridge
桥接到远程/本地 Codex CLI
"""

import json
import asyncio
from pathlib import Path
from base_bridge import BaseBridge, BridgeResponse


class CodexBridge(BaseBridge):
    """Codex CLI 桥接"""

    async def execute(self, prompt: str, working_dir: str,
                      session_id: str = None, **kwargs) -> BridgeResponse:
        """执行 Codex 任务"""

        sandbox = kwargs.get('sandbox', 'read-only')
        model = kwargs.get('model', 'gpt-4')

        # 构建命令
        cmd_parts = [
            'codex',
            f'--approval-mode {sandbox}',
            f'--model {model}',
            '--output-format json',
        ]

        if session_id:
            cmd_parts.append(f'--session {session_id}')

        # 转义 prompt
        escaped_prompt = prompt.replace('"', '\\"').replace("'", "\\'")
        cmd_parts.append(f'"{escaped_prompt}"')

        command = ' '.join(cmd_parts)

        # 执行
        if self.protocol == 'ssh':
            returncode, stdout, stderr = await self._run_ssh_command(
                f'cd {working_dir} && {command}'
            )
        elif self.protocol == 'docker':
            container = self.config.get('container', self.service_id)
            returncode, stdout, stderr = await self._run_docker_command(
                f'cd {working_dir} && {command}', container
            )
        else:
            # 本地执行
            proc = await asyncio.create_subprocess_shell(
                f'cd {working_dir} && {command}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_bytes, stderr_bytes = await proc.communicate()
            returncode = proc.returncode
            stdout, stderr = stdout_bytes.decode(), stderr_bytes.decode()

        # 解析响应
        try:
            result = json.loads(stdout)
            return BridgeResponse(
                success=result.get('success', False),
                session_id=result.get('session_id', session_id or ''),
                message=result.get('message', ''),
                tokens_used=result.get('tokens_used', 0),
                output=result.get('output')
            )
        except json.JSONDecodeError:
            return BridgeResponse(
                success=returncode == 0,
                session_id=session_id or '',
                message=stdout,
                error=stderr if stderr else None
            )

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if self.protocol == 'ssh':
                returncode, _, _ = await self._run_ssh_command('which codex')
            else:
                proc = await asyncio.create_subprocess_shell(
                    'which codex',
                    stdout=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                returncode = proc.returncode

            return returncode == 0
        except Exception:
            return False


# CLI 入口
if __name__ == "__main__":
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description="Codex Bridge")
    parser.add_argument("--config", required=True, help="Service config file")
    parser.add_argument("--PROMPT", required=True, help="Task prompt")
    parser.add_argument("--cd", required=True, help="Working directory")
    parser.add_argument("--SESSION_ID", help="Session ID for multi-turn")
    parser.add_argument("--sandbox", default="read-only", help="Sandbox mode")
    parser.add_argument("--health-check", action="store_true", help="Run health check")

    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    bridge = CodexBridge(config['service']['id'], config)

    if args.health_check:
        result = asyncio.run(bridge.health_check())
        print(f"Health: {'OK' if result else 'FAILED'}")
    else:
        response = asyncio.run(bridge.execute(
            prompt=args.PROMPT,
            working_dir=args.cd,
            session_id=args.SESSION_ID,
            sandbox=args.sandbox
        ))
        print(json.dumps({
            'success': response.success,
            'session_id': response.session_id,
            'message': response.message,
            'tokens_used': response.tokens_used,
            'output': response.output,
            'error': response.error
        }, indent=2))
```

## 8. Git 配置与代码隔离

### 8.1 Git 分支策略

```
main                    # 代码分支
├── code/
├── skills/
└── README.md

config                  # 配置分支
├── services/
├── routing/
├── token-budget/
└── global.yaml
```

### 8.2 初始化脚本

`scripts/init-repo.sh`:

```bash
#!/bin/bash
# 初始化多分支仓库

set -e

echo "=== 初始化 Multi-AI Orchestrator 仓库 ==="

# 1. 初始化 Git
git init

# 2. 创建 main 分支（代码）
git checkout -b main

# 创建代码目录结构
mkdir -p code/core code/bridges code/utils
mkdir -p skills/orchestrator/scripts
mkdir -p scripts
mkdir -p data
mkdir -p logs

# 添加 .gitignore
cat > .gitignore << 'EOF'
# 数据和日志
data/
logs/
*.db
*.log

# Python
__pycache__/
*.pyc
.venv/
venv/

# 敏感信息
*.key
*.pem
secrets/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

git add .
git commit -m "Initial commit: code structure"

# 3. 创建 config 分支
git checkout --orphan config

# 清空工作区
git rm -rf . 2>/dev/null || true

# 创建配置目录结构
mkdir -p config/services config/routing config/token-budget

# 创建示例配置
cat > config/global.yaml << 'EOF'
orchestrator:
  name: multi-ai-orchestrator
  version: "1.0.0"

discovery:
  auto_register: true
  config_path: ./config/services/

token_management:
  global_daily_limit: 500000
  warning_threshold: 0.8

routing:
  default_strategy: capability_match
  fallback_enabled: true
EOF

cat > config/services/.gitkeep << 'EOF'
# 服务配置文件存放目录
# 格式: S001-service-name.yaml
EOF

git add .
git commit -m "Initial commit: config structure"

# 4. 返回 main 分支
git checkout main

echo "=== 仓库初始化完成 ==="
echo "代码分支: main"
echo "配置分支: config"
echo ""
echo "添加服务配置:"
echo "  git checkout config"
echo "  # 编辑 config/services/S001-xxx.yaml"
echo "  git commit -am 'Add service S001'"
echo "  git checkout main"
```

### 8.3 配置同步脚本

`scripts/sync-config.sh`:

```bash
#!/bin/bash
# 同步配置分支到工作目录

CONFIG_BRANCH=${1:-config}
CONFIG_DIR=${2:-./config}

echo "Syncing config from branch: $CONFIG_BRANCH"

# 检出配置分支的文件到工作目录
git checkout $CONFIG_BRANCH -- config/

echo "Config synced to $CONFIG_DIR"

# 列出同步的服务配置
echo "Services:"
ls -1 $CONFIG_DIR/services/*.yaml 2>/dev/null || echo "  No services configured"
```

## 9. CLAUDE.md 全局协议

`~/.claude/CLAUDE.md` (或项目根目录):

```markdown
# Multi-AI Orchestrator Protocol

## Language Settings
- Tool interaction: English
- User communication: 中文

## Available Services

当检测到以下 Skills 时自动加载：
- `orchestrator` - 核心编排器
- `service-s001-*` - Codex 服务
- `service-s002-*` - Gemini 服务
- `service-s003-*` - Claude 服务

## Workflow Protocol

### Phase 1: Task Analysis
1. 分析用户需求
2. 确定任务类型和所需能力
3. 查询 Token 预算

### Phase 2: Service Selection
1. 调用 `@orchestrator route` 获取路由决策
2. 检查目标服务健康状态
3. 验证 Token 预算

### Phase 3: Task Execution
1. 调用选定服务执行任务
2. 收集返回的 unified diff
3. 记录 Token 使用

### Phase 4: Result Integration
1. 审查外部模型输出
2. 重构为生产代码
3. 应用代码变更

### Phase 5: Verification
1. 运行测试
2. 代码审查
3. 提交变更

## Security Rules
- 外部服务只能返回 unified diff，不能直接写文件
- 所有文件修改由本地 Claude Code 执行
- 敏感文件（.env, secrets/）禁止发送到外部服务

## Token Management
- 每次调用前检查预算
- 超过 80% 预算时警告
- 超过 100% 时阻止调用
```

## 10. 快速开始

### 10.1 安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/multi-ai-orchestrator.git
cd multi-ai-orchestrator

# 2. 初始化
./scripts/init-repo.sh

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 安装 Skills
cp -r skills/* ~/.claude/skills/
```

### 10.2 添加服务

```bash
# 1. 切换到配置分支
git checkout config

# 2. 创建服务配置
cat > config/services/S001-codex-mac.yaml << 'EOF'
service:
  id: S001
  name: codex-mac-mini
  type: codex
  enabled: true

connection:
  host: mac-mini.local
  port: 22
  protocol: ssh
  auth:
    type: ssh-key
    user: developer

capabilities:
  - code_generation
  - debugging

specialties:
  languages: [python, javascript]
  domains: [backend]

token_budget:
  daily_limit: 100000

security:
  sandbox: read-only
EOF

# 3. 提交
git commit -am "Add service S001: Codex on Mac Mini"

# 4. 返回 main 并同步
git checkout main
./scripts/sync-config.sh
```

### 10.3 使用示例

```bash
# 在 Claude Code 中

# 查看可用服务
@orchestrator list

# 路由任务
@orchestrator route --task "实现用户认证 API" --type code_generation --lang python

# 检查 Token 使用
@orchestrator tokens --status

# 直接调用特定服务
@service-s001-codex execute --PROMPT "优化这个算法的时间复杂度" --cd /workspace
```

## 11. 参考资源

- [GuDaStudio/skills](https://github.com/GuDaStudio/skills) - 原始 Skills 项目
- [GuDaStudio/collaborating-with-codex](https://github.com/GuDaStudio/collaborating-with-codex) - Codex 集成
- [Claude Code Skills 文档](https://claude.com/blog/skills)
- [claude-flow](https://github.com/ruvnet/claude-flow) - 多代理编排平台

---

*本方案基于 GuDaStudio/skills 项目架构设计*
