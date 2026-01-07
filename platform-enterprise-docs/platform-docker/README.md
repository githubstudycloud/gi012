# Platform Enterprise Docker 部署

## 快速启动

### 前置条件
- Docker 24.0+
- Docker Compose 2.20+
- 至少 8GB 可用内存

### 启动所有服务

```bash
# 启动基础设施
docker compose up -d postgres redis minio rabbitmq nacos

# 等待基础设施就绪（约30秒）
sleep 30

# 启动后端服务
docker compose up -d platform-gateway platform-auth platform-user

# 启动前端
docker compose up -d platform-ui
```

### 一键启动

```bash
docker compose up -d
```

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| platform-ui | 80/443 | 前端服务 |
| platform-gateway | 8080 | API 网关 |
| platform-auth | 9100 | 认证服务 |
| platform-user | 9200 | 用户服务 |
| platform-business | 9300 | 业务服务 |
| platform-file | 9400 | 文件服务 |
| platform-message | 9500 | 消息服务 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| MinIO | 9000/9001 | 对象存储 |
| RabbitMQ | 5672/15672 | 消息队列 |
| Nacos | 8848 | 服务发现/配置中心 |

## 默认账号

### 系统管理员
- 用户名: admin
- 密码: admin123

### 数据库
- 用户名: platform
- 密码: Platform@2024

### Nacos
- 用户名: nacos
- 密码: nacos

### MinIO
- Access Key: platform
- Secret Key: Platform@2024

### RabbitMQ
- 用户名: platform
- 密码: Platform@2024

## 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f [service-name]

# 停止所有服务
docker compose down

# 停止并删除数据卷
docker compose down -v

# 重建单个服务
docker compose up -d --build [service-name]

# 进入容器
docker compose exec [service-name] sh
```

## 生产环境部署

1. 修改所有默认密码
2. 启用 HTTPS（取消 nginx.conf 中的 SSL 注释）
3. 配置外部数据库（PostgreSQL 主从）
4. 配置 Redis 集群
5. 配置 Nacos 集群
6. 调整 JVM 参数
7. 配置日志收集（ELK/Loki）
8. 配置监控告警（Prometheus/Grafana）

## 目录结构

```
platform-docker/
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile.backend      # 后端服务 Dockerfile
├── Dockerfile.frontend     # 前端 Dockerfile
├── nginx/
│   ├── nginx.conf          # Nginx 配置
│   └── ssl/                # SSL 证书目录
└── sql/
    ├── 00-init-nacos.sql   # Nacos 数据库初始化
    ├── 01-init-database.sql # 业务数据库初始化
    └── 02-init-data.sql    # 初始数据
```
