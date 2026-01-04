#!/usr/bin/env python3
"""
AI Service Hub - 简化版多 AI 服务管理中心
带 Web 图形界面的 AI 服务编排工具
"""

import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, date
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

CONFIG_FILE = Path(__file__).parent / 'config.json'
USAGE_FILE = Path(__file__).parent / 'usage.json'


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "services": [],
        "token_budget": {"daily_limit": 500000}
    }


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_usage():
    """加载使用记录"""
    if USAGE_FILE.exists():
        with open(USAGE_FILE) as f:
            return json.load(f)
    return {"daily": {}, "total": {}}


def save_usage(usage):
    """保存使用记录"""
    with open(USAGE_FILE, 'w') as f:
        json.dump(usage, f, indent=2)


# ==================== API 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/services', methods=['GET'])
def get_services():
    """获取所有服务"""
    config = load_config()
    return jsonify(config.get('services', []))


@app.route('/api/services', methods=['POST'])
def add_service():
    """添加服务"""
    data = request.json
    config = load_config()

    # 生成 ID
    existing_ids = [s['id'] for s in config['services']]
    new_id = f"{len(existing_ids) + 1:03d}"

    service = {
        "id": new_id,
        "name": data['name'],
        "type": data['type'],
        "host": data['host'],
        "port": data.get('port', 22),
        "protocol": data.get('protocol', 'ssh'),
        "user": data.get('user', ''),
        "enabled": True,
        "status": "unknown",
        "created": datetime.now().isoformat()
    }

    config['services'].append(service)
    save_config(config)

    return jsonify({"success": True, "service": service})


@app.route('/api/services/<service_id>', methods=['PUT'])
def update_service(service_id):
    """更新服务"""
    data = request.json
    config = load_config()

    for service in config['services']:
        if service['id'] == service_id:
            service.update(data)
            break

    save_config(config)
    return jsonify({"success": True})


@app.route('/api/services/<service_id>', methods=['DELETE'])
def delete_service(service_id):
    """删除服务"""
    config = load_config()
    config['services'] = [s for s in config['services'] if s['id'] != service_id]
    save_config(config)
    return jsonify({"success": True})


@app.route('/api/services/<service_id>/test', methods=['POST'])
def test_service(service_id):
    """测试服务连接"""
    config = load_config()
    service = next((s for s in config['services'] if s['id'] == service_id), None)

    if not service:
        return jsonify({"success": False, "error": "Service not found"})

    try:
        if service['protocol'] == 'ssh':
            # SSH 连接测试
            cmd = f"ssh -o ConnectTimeout=5 -o BatchMode=yes {service.get('user', '')}@{service['host']} echo ok 2>&1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            success = 'ok' in result.stdout
        elif service['protocol'] == 'docker':
            # Docker 连接测试
            cmd = f"docker exec {service['host']} echo ok 2>&1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            success = 'ok' in result.stdout
        elif service['protocol'] == 'local':
            success = True
        else:
            success = False

        # 更新状态
        service['status'] = 'online' if success else 'offline'
        service['last_check'] = datetime.now().isoformat()
        save_config(config)

        return jsonify({"success": success, "status": service['status']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/execute', methods=['POST'])
def execute_task():
    """执行任务"""
    data = request.json
    service_id = data.get('service_id')
    task = data.get('task')

    config = load_config()
    service = next((s for s in config['services'] if s['id'] == service_id), None)

    if not service:
        return jsonify({"success": False, "error": "Service not found"})

    try:
        # 构建命令
        if service['type'] == 'codex':
            cmd = f'codex "{task}"'
        elif service['type'] == 'gemini':
            cmd = f'gemini "{task}"'
        elif service['type'] == 'claude':
            cmd = f'claude -p "{task}"'
        else:
            cmd = f'echo "Unknown service type"'

        # 执行
        if service['protocol'] == 'ssh':
            full_cmd = f"ssh {service.get('user', '')}@{service['host']} '{cmd}'"
        elif service['protocol'] == 'docker':
            full_cmd = f"docker exec {service['host']} {cmd}"
        else:
            full_cmd = cmd

        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=300)

        # 记录使用
        record_usage(service_id, len(task) * 2)  # 简单估算 token

        return jsonify({
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/usage', methods=['GET'])
def get_usage():
    """获取使用统计"""
    usage = load_usage()
    config = load_config()

    today = date.today().isoformat()
    daily = usage.get('daily', {}).get(today, {})

    result = {
        "today": daily,
        "total": usage.get('total', {}),
        "budget": config.get('token_budget', {})
    }

    return jsonify(result)


def record_usage(service_id, tokens):
    """记录使用量"""
    usage = load_usage()
    today = date.today().isoformat()

    if 'daily' not in usage:
        usage['daily'] = {}
    if today not in usage['daily']:
        usage['daily'][today] = {}
    if service_id not in usage['daily'][today]:
        usage['daily'][today][service_id] = 0

    usage['daily'][today][service_id] += tokens

    if 'total' not in usage:
        usage['total'] = {}
    if service_id not in usage['total']:
        usage['total'][service_id] = 0

    usage['total'][service_id] += tokens

    save_usage(usage)


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置"""
    return jsonify(load_config())


@app.route('/api/config', methods=['PUT'])
def update_config():
    """更新配置"""
    data = request.json
    config = load_config()
    config.update(data)
    save_config(config)
    return jsonify({"success": True})


if __name__ == '__main__':
    print("=" * 50)
    print("  AI Service Hub - 多 AI 服务管理中心")
    print("=" * 50)
    print(f"  访问地址: http://localhost:8080")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8080, debug=True)
