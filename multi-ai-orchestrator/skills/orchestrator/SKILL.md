# Multi-AI Orchestrator Skill

## Description

This skill manages multiple AI services (Codex, Gemini, Claude Code) running on
different machines (Linux, Docker, Mac). It handles task routing, token budget
management, and service health monitoring.

## Capabilities

- **Service Registry**: Register and manage multiple AI services
- **Task Routing**: Route tasks to appropriate services based on capabilities
- **Token Management**: Track and control token usage across all services
- **Health Monitoring**: Monitor service availability and performance
- **Result Aggregation**: Collect and merge results from multiple services

## Available Commands

### List Services
```bash
python scripts/service_registry.py list [--type <service_type>]
```
Lists all registered services with their status.

### Register Service
```bash
python scripts/service_registry.py register --config <config_file>
```
Register a new service from configuration file.

### Route Task
```bash
python scripts/router.py --task "<task>" --type <task_type> [--lang <language>] [--domain <domain>]
```
Route a task to appropriate service(s).

### Check Token Budget
```bash
python scripts/token_manager.py status [--service <service_id>]
```
Check token usage and remaining budget.

### Health Check
```bash
python scripts/service_registry.py health [--id <service_id>]
```
Check health status of services.

## Usage Examples

### Route a coding task
```
@orchestrator route --task "Implement user authentication API" --type code_generation --lang python
```

### Check all services
```
@orchestrator list
```

### Get token usage report
```
@orchestrator tokens --report daily
```

## Configuration

Services are configured in `config/services/` directory.
Routing rules are in `config/routing/task-routing.yaml`.
Token budgets are in `config/token-budget/per-service-limits.yaml`.

## Security

- External services return unified diff patches only
- No direct filesystem writes from external services
- Sensitive files (.env, secrets/) are never sent to external services
- All changes are reviewed and applied by local Claude Code
