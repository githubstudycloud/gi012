#!/bin/bash

# Platform Enterprise 一键部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    log_info "Docker 版本: $(docker --version)"
    log_info "Docker Compose 版本: $(docker compose version)"
}

# 检查端口是否被占用
check_ports() {
    local ports=(80 443 5432 6379 8080 8848 9000 9001 9100 9200 9300 9400 9500 5672 15672)

    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warn "端口 $port 已被占用"
        fi
    done
}

# 创建必要的目录
create_dirs() {
    log_info "创建必要的目录..."
    mkdir -p nginx/ssl
}

# 启动基础设施
start_infra() {
    log_info "启动基础设施服务..."
    docker compose up -d postgres redis minio rabbitmq

    log_info "等待数据库就绪..."
    sleep 15

    log_info "启动 Nacos..."
    docker compose up -d nacos

    log_info "等待 Nacos 就绪..."
    sleep 20
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    docker compose up -d platform-gateway platform-auth platform-user platform-business platform-file platform-message

    log_info "等待后端服务就绪..."
    sleep 30
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."
    docker compose up -d platform-ui
}

# 健康检查
health_check() {
    log_info "进行健康检查..."

    local services=("postgres:5432" "redis:6379" "nacos:8848")

    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        if docker compose exec -T $name sh -c "exit 0" 2>/dev/null; then
            log_info "$name 运行正常"
        else
            log_warn "$name 可能存在问题"
        fi
    done
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker compose ps
}

# 显示访问信息
show_info() {
    echo ""
    echo "=========================================="
    echo "         Platform Enterprise 部署完成"
    echo "=========================================="
    echo ""
    echo "访问地址:"
    echo "  - 前端: http://localhost"
    echo "  - API网关: http://localhost:8080"
    echo "  - Nacos: http://localhost:8848/nacos"
    echo "  - MinIO: http://localhost:9001"
    echo "  - RabbitMQ: http://localhost:15672"
    echo ""
    echo "默认账号:"
    echo "  - 系统管理员: admin / admin123"
    echo "  - Nacos: nacos / nacos"
    echo "  - MinIO: platform / Platform@2024"
    echo "  - RabbitMQ: platform / Platform@2024"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    case "${1:-all}" in
        "check")
            check_docker
            check_ports
            ;;
        "infra")
            check_docker
            create_dirs
            start_infra
            ;;
        "backend")
            start_backend
            ;;
        "frontend")
            start_frontend
            ;;
        "all")
            check_docker
            create_dirs
            start_infra
            start_backend
            start_frontend
            health_check
            show_status
            show_info
            ;;
        "status")
            show_status
            ;;
        "stop")
            log_info "停止所有服务..."
            docker compose down
            ;;
        "restart")
            log_info "重启所有服务..."
            docker compose restart
            ;;
        "logs")
            docker compose logs -f ${2:-}
            ;;
        *)
            echo "用法: $0 {check|infra|backend|frontend|all|status|stop|restart|logs [service]}"
            exit 1
            ;;
    esac
}

main "$@"
