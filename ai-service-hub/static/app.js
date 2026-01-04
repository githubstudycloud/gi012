/**
 * AI Service Hub - 前端逻辑
 */

// API 基础路径
const API = '';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    loadServices();
    loadUsage();
});

// ==================== 服务管理 ====================

/**
 * 加载服务列表
 */
async function loadServices() {
    try {
        const response = await fetch(`${API}/api/services`);
        const services = await response.json();
        renderServices(services);
        updateServiceSelect(services);
    } catch (error) {
        console.error('加载服务失败:', error);
    }
}

/**
 * 渲染服务列表
 */
function renderServices(services) {
    const container = document.getElementById('services-list');

    if (services.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>暂无服务，点击上方按钮添加</p>
            </div>
        `;
        return;
    }

    container.innerHTML = services.map(service => `
        <div class="service-card" data-id="${service.id}">
            <div class="service-header">
                <span class="service-name">${getTypeIcon(service.type)} ${service.name}</span>
                <span class="service-status status-${service.status || 'unknown'}">
                    ${getStatusText(service.status)}
                </span>
            </div>
            <div class="service-info">
                <p>类型: ${getTypeName(service.type)}</p>
                <p>协议: ${service.protocol}</p>
                <p>地址: ${service.host}${service.port ? ':' + service.port : ''}</p>
            </div>
            <div class="service-actions">
                <button class="btn btn-small" onclick="testService('${service.id}')">测试连接</button>
                <button class="btn btn-small" onclick="editService('${service.id}')">编辑</button>
                <button class="btn btn-small btn-danger" onclick="deleteService('${service.id}')">删除</button>
            </div>
        </div>
    `).join('');
}

/**
 * 获取服务类型图标
 */
function getTypeIcon(type) {
    const icons = {
        'codex': '🟢',
        'gemini': '🔵',
        'claude': '🟣'
    };
    return icons[type] || '⚪';
}

/**
 * 获取服务类型名称
 */
function getTypeName(type) {
    const names = {
        'codex': 'Codex CLI',
        'gemini': 'Gemini CLI',
        'claude': 'Claude Code'
    };
    return names[type] || type;
}

/**
 * 获取状态文本
 */
function getStatusText(status) {
    const texts = {
        'online': '在线',
        'offline': '离线',
        'unknown': '未知'
    };
    return texts[status] || '未知';
}

/**
 * 更新服务选择下拉框
 */
function updateServiceSelect(services) {
    const select = document.getElementById('task-service');
    select.innerHTML = '<option value="">选择服务...</option>' +
        services.map(s => `<option value="${s.id}">${s.name} (${getTypeName(s.type)})</option>`).join('');
}

/**
 * 显示添加服务模态框
 */
function showAddModal() {
    document.getElementById('modal-title').textContent = '添加服务';
    document.getElementById('service-id').value = '';
    document.getElementById('service-form').reset();
    document.getElementById('service-modal').style.display = 'flex';
    updateHostLabel();
}

/**
 * 编辑服务
 */
async function editService(id) {
    try {
        const response = await fetch(`${API}/api/services`);
        const services = await response.json();
        const service = services.find(s => s.id === id);

        if (service) {
            document.getElementById('modal-title').textContent = '编辑服务';
            document.getElementById('service-id').value = service.id;
            document.getElementById('service-name').value = service.name;
            document.getElementById('service-type').value = service.type;
            document.getElementById('service-protocol').value = service.protocol;
            document.getElementById('service-host').value = service.host;
            document.getElementById('service-user').value = service.user || '';
            document.getElementById('service-port').value = service.port || 22;
            document.getElementById('service-modal').style.display = 'flex';
            updateHostLabel();
        }
    } catch (error) {
        console.error('加载服务详情失败:', error);
    }
}

/**
 * 关闭模态框
 */
function closeModal() {
    document.getElementById('service-modal').style.display = 'none';
}

/**
 * 更新主机标签
 */
function updateHostLabel() {
    const protocol = document.getElementById('service-protocol').value;
    const label = document.getElementById('host-label');
    const userGroup = document.getElementById('user-group');
    const portGroup = document.getElementById('port-group');

    if (protocol === 'docker') {
        label.textContent = '容器名称';
        userGroup.style.display = 'none';
        portGroup.style.display = 'none';
    } else if (protocol === 'local') {
        label.textContent = '本地路径 (可选)';
        userGroup.style.display = 'none';
        portGroup.style.display = 'none';
    } else {
        label.textContent = '主机地址';
        userGroup.style.display = 'block';
        portGroup.style.display = 'block';
    }
}

/**
 * 保存服务
 */
async function saveService(event) {
    event.preventDefault();

    const id = document.getElementById('service-id').value;
    const data = {
        name: document.getElementById('service-name').value,
        type: document.getElementById('service-type').value,
        protocol: document.getElementById('service-protocol').value,
        host: document.getElementById('service-host').value,
        user: document.getElementById('service-user').value,
        port: parseInt(document.getElementById('service-port').value) || 22
    };

    try {
        const url = id ? `${API}/api/services/${id}` : `${API}/api/services`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            closeModal();
            loadServices();
        } else {
            alert('保存失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        console.error('保存服务失败:', error);
        alert('保存失败');
    }
}

/**
 * 删除服务
 */
async function deleteService(id) {
    if (!confirm('确定要删除此服务吗？')) return;

    try {
        const response = await fetch(`${API}/api/services/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            loadServices();
        } else {
            alert('删除失败');
        }
    } catch (error) {
        console.error('删除服务失败:', error);
    }
}

/**
 * 测试服务连接
 */
async function testService(id) {
    const card = document.querySelector(`.service-card[data-id="${id}"]`);
    const btn = card.querySelector('button');
    const originalText = btn.textContent;
    btn.innerHTML = '<span class="loading"></span>';
    btn.disabled = true;

    try {
        const response = await fetch(`${API}/api/services/${id}/test`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            alert('连接成功！');
        } else {
            alert('连接失败: ' + (result.error || '无法连接'));
        }

        loadServices(); // 刷新状态
    } catch (error) {
        console.error('测试连接失败:', error);
        alert('测试失败');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// ==================== 任务执行 ====================

/**
 * 执行任务
 */
async function executeTask() {
    const serviceId = document.getElementById('task-service').value;
    const task = document.getElementById('task-input').value.trim();

    if (!serviceId) {
        alert('请选择服务');
        return;
    }

    if (!task) {
        alert('请输入任务描述');
        return;
    }

    const outputBox = document.getElementById('task-output');
    const outputContent = document.getElementById('output-content');

    outputBox.style.display = 'block';
    outputContent.textContent = '执行中...';

    try {
        const response = await fetch(`${API}/api/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                service_id: serviceId,
                task: task
            })
        });

        const result = await response.json();

        if (result.success) {
            outputContent.textContent = result.output || '(无输出)';
            outputContent.style.color = '#22c55e';
        } else {
            outputContent.textContent = '错误: ' + (result.error || result.output || '执行失败');
            outputContent.style.color = '#ef4444';
        }

        loadUsage(); // 刷新使用统计
    } catch (error) {
        console.error('执行任务失败:', error);
        outputContent.textContent = '请求失败: ' + error.message;
        outputContent.style.color = '#ef4444';
    }
}

// ==================== 使用统计 ====================

/**
 * 加载使用统计
 */
async function loadUsage() {
    try {
        const response = await fetch(`${API}/api/usage`);
        const usage = await response.json();
        renderUsage(usage);
    } catch (error) {
        console.error('加载使用统计失败:', error);
    }
}

/**
 * 渲染使用统计
 */
function renderUsage(usage) {
    const container = document.getElementById('usage-stats');

    // 计算今日总量
    const todayTotal = Object.values(usage.today || {}).reduce((a, b) => a + b, 0);
    const totalAll = Object.values(usage.total || {}).reduce((a, b) => a + b, 0);
    const dailyLimit = usage.budget?.daily_limit || 500000;
    const remaining = Math.max(0, dailyLimit - todayTotal);

    container.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${formatNumber(todayTotal)}</div>
            <div class="stat-label">今日使用 Token</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(remaining)}</div>
            <div class="stat-label">今日剩余额度</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(totalAll)}</div>
            <div class="stat-label">累计使用 Token</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(dailyLimit)}</div>
            <div class="stat-label">每日限额</div>
        </div>
    `;
}

/**
 * 格式化数字
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}
