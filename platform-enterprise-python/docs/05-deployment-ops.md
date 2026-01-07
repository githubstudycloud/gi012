# Platform Enterprise Python - 部署与运维

## 1. 部署架构

### 1.1 环境规划

| 环境 | 用途 | 域名 | 集群规模 |
|------|------|------|----------|
| Development | 本地开发 | localhost | Docker Compose |
| Staging | 预发布测试 | staging.platform.io | 2 节点 |
| Production | 生产环境 | api.platform.io | 3+ 节点 |

### 1.2 生产架构图

```
                                    ┌─────────────────────────────────────┐
                                    │          CDN / WAF                  │
                                    │      (Cloudflare / AWS WAF)         │
                                    └──────────────┬──────────────────────┘
                                                   │
                                    ┌──────────────▼──────────────────────┐
                                    │        Load Balancer                │
                                    │     (Nginx / AWS ALB / Traefik)     │
                                    └──────────────┬──────────────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
         ┌──────────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼──────────┐
         │   K8s Node 1       │         │   K8s Node 2       │         │   K8s Node 3       │
         │ ┌───────────────┐  │         │ ┌───────────────┐  │         │ ┌───────────────┐  │
         │ │ platform-api  │  │         │ │ platform-api  │  │         │ │ platform-api  │  │
         │ │ (3 replicas)  │  │         │ │ (3 replicas)  │  │         │ │ (3 replicas)  │  │
         │ └───────────────┘  │         │ └───────────────┘  │         │ └───────────────┘  │
         │ ┌───────────────┐  │         │ ┌───────────────┐  │         │ ┌───────────────┐  │
         │ │ platform-auth │  │         │ │ platform-user │  │         │ │platform-worker│  │
         │ └───────────────┘  │         │ └───────────────┘  │         │ └───────────────┘  │
         └────────────────────┘         └────────────────────┘         └────────────────────┘
                    │                              │                              │
                    └──────────────────────────────┼──────────────────────────────┘
                                                   │
         ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
         │                                         │                                         │
         ▼                                         ▼                                         ▼
┌─────────────────┐                     ┌─────────────────┐                     ┌─────────────────┐
│   PostgreSQL    │                     │     Redis       │                     │   RabbitMQ      │
│   Primary +     │                     │   Cluster       │                     │   Cluster       │
│   2 Replicas    │                     │   (6 nodes)     │                     │   (3 nodes)     │
└─────────────────┘                     └─────────────────┘                     └─────────────────┘
```

---

## 2. Docker 容器化

### 2.1 多阶段构建 Dockerfile

```dockerfile
# deploy/docker/Dockerfile.api
# ============================================
# 阶段 1: 构建依赖
# ============================================
FROM python:3.12-slim AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 复制依赖文件
COPY pyproject.toml uv.lock ./
COPY libs/ libs/
COPY services/platform-api/ services/platform-api/

# 安装依赖 (不含开发依赖)
RUN uv sync --frozen --no-dev --no-editable

# ============================================
# 阶段 2: 运行时镜像
# ============================================
FROM python:3.12-slim AS runtime

# 安全: 创建非 root 用户
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# 复制虚拟环境和代码
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/services/platform-api/src /app/src

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "platform_api.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output"]
```

### 2.2 Docker Compose (开发环境)

```yaml
# deploy/docker/docker-compose.dev.yml
version: "3.9"

services:
  # ===== 基础设施 =====
  postgres:
    image: postgres:16-alpine
    container_name: platform-postgres
    environment:
      POSTGRES_USER: platform
      POSTGRES_PASSWORD: platform_dev_password
      POSTGRES_DB: platform
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U platform"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: platform-redis
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    container_name: platform-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: platform
      RABBITMQ_DEFAULT_PASS: platform_dev_password
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 30s
      timeout: 10s
      retries: 5

  # ===== 可观测性 =====
  jaeger:
    image: jaegertracing/all-in-one:1.53
    container_name: platform-jaeger
    environment:
      COLLECTOR_OTLP_ENABLED: true
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP

  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: platform-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:10.2.0
    container_name: platform-grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_USERS_ALLOW_SIGN_UP: false
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: platform-network
```

### 2.3 Docker Compose (生产模拟)

```yaml
# deploy/docker/docker-compose.prod.yml
version: "3.9"

services:
  platform-api:
    build:
      context: ../..
      dockerfile: deploy/docker/Dockerfile.api
    image: platform-api:${VERSION:-latest}
    container_name: platform-api
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql+asyncpg://platform:${DB_PASSWORD}@postgres:5432/platform
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  platform-auth:
    build:
      context: ../..
      dockerfile: deploy/docker/Dockerfile.auth
    image: platform-auth:${VERSION:-latest}
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql+asyncpg://platform:${DB_PASSWORD}@postgres:5432/platform
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis

  platform-worker:
    build:
      context: ../..
      dockerfile: deploy/docker/Dockerfile.worker
    image: platform-worker:${VERSION:-latest}
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql+asyncpg://platform:${DB_PASSWORD}@postgres:5432/platform
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - rabbitmq
    deploy:
      replicas: 2
```

---

## 3. Kubernetes 部署

### 3.1 命名空间与资源配额

```yaml
# deploy/kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: platform
  labels:
    name: platform
    istio-injection: enabled
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: platform-quota
  namespace: platform
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: platform-limits
  namespace: platform
spec:
  limits:
    - default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      type: Container
```

### 3.2 ConfigMap 与 Secret

```yaml
# deploy/kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: platform-config
  namespace: platform
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "https://app.platform.io,https://admin.platform.io"
  DB_POOL_SIZE: "10"
  DB_MAX_OVERFLOW: "20"
  REDIS_MAX_CONNECTIONS: "50"
---
# deploy/kubernetes/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: platform-secrets
  namespace: platform
type: Opaque
stringData:
  DATABASE_URL: "postgresql+asyncpg://platform:PASSWORD@postgres-primary:5432/platform"
  REDIS_URL: "redis://:PASSWORD@redis-master:6379/0"
  SECRET_KEY: "your-super-secret-key-at-least-32-chars"
  JWT_SECRET_KEY: "your-jwt-secret-key-at-least-32-chars"
```

### 3.3 Deployment

```yaml
# deploy/kubernetes/deployment-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: platform-api
  namespace: platform
  labels:
    app: platform-api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: platform-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: platform-api
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: platform-api
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
        - name: platform-api
          image: registry.platform.io/platform-api:v1.0.0
          imagePullPolicy: Always

          ports:
            - name: http
              containerPort: 8000
              protocol: TCP

          envFrom:
            - configMapRef:
                name: platform-config
            - secretRef:
                name: platform-secrets

          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "512Mi"

          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 5
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3

          startupProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 30

          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]

          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

          volumeMounts:
            - name: tmp
              mountPath: /tmp

      volumes:
        - name: tmp
          emptyDir: {}

      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: platform-api
                topologyKey: kubernetes.io/hostname

      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: platform-api

      terminationGracePeriodSeconds: 30
```

### 3.4 Service

```yaml
# deploy/kubernetes/service-api.yaml
apiVersion: v1
kind: Service
metadata:
  name: platform-api
  namespace: platform
  labels:
    app: platform-api
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: 8000
      protocol: TCP
  selector:
    app: platform-api
```

### 3.5 Ingress

```yaml
# deploy/kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: platform-ingress
  namespace: platform
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.platform.io
      secretName: platform-tls
  rules:
    - host: api.platform.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: platform-api
                port:
                  number: 80
```

### 3.6 HorizontalPodAutoscaler

```yaml
# deploy/kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: platform-api-hpa
  namespace: platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: platform-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

### 3.7 PodDisruptionBudget

```yaml
# deploy/kubernetes/pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: platform-api-pdb
  namespace: platform
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: platform-api
```

---

## 4. CI/CD Pipeline

### 4.1 GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  UV_CACHE_DIR: /tmp/.uv-cache
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
          enable-cache: true

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run Ruff
        run: uv run ruff check .

      - name: Run Ruff Format
        run: uv run ruff format --check .

      - name: Run MyPy
        run: uv run mypy .

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
          enable-cache: true

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
        run: uv run pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  build:
    name: Build & Push
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.REGISTRY_URL }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.REGISTRY_URL }}/platform-api
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: deploy/docker/Dockerfile.api
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    environment: staging

    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy to staging
        run: |
          kubectl set image deployment/platform-api \
            platform-api=${{ secrets.REGISTRY_URL }}/platform-api:${{ github.sha }} \
            -n platform-staging

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/platform-api \
            -n platform-staging --timeout=300s
```

### 4.2 发布流程

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog
        id: changelog
        uses: orhun/git-cliff-action@v3
        with:
          config: cliff.toml
          args: --latest --strip header

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body: ${{ steps.changelog.outputs.content }}
          draft: false
          prerelease: ${{ contains(github.ref, '-rc') || contains(github.ref, '-beta') }}

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: release
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy to production
        run: |
          kubectl set image deployment/platform-api \
            platform-api=${{ secrets.REGISTRY_URL }}/platform-api:${{ github.ref_name }} \
            -n platform

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/platform-api \
            -n platform --timeout=600s
```

---

## 5. 监控与告警

### 5.1 健康检查端点

```python
# platform_api/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
async def liveness():
    """存活探针 - 检查应用是否运行"""
    return {"status": "alive"}


@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """就绪探针 - 检查应用是否准备好接收流量"""
    checks = {
        "database": False,
        "redis": False,
    }

    # 检查数据库
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass

    # 检查 Redis
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = True
    except Exception:
        pass

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
        },
    )


@router.get("/metrics")
async def metrics():
    """Prometheus 指标端点"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
```

### 5.2 Prometheus 配置

```yaml
# deploy/docker/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: 'platform-api'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: pod
```

### 5.3 告警规则

```yaml
# deploy/prometheus/rules/platform.yml
groups:
  - name: platform-alerts
    rules:
      # 高错误率
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) /
          sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} over the last 5 minutes"

      # 高延迟
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P99 latency is {{ $value | humanizeDuration }}"

      # Pod 重启
      - alert: PodRestarting
        expr: |
          increase(kube_pod_container_status_restarts_total{namespace="platform"}[1h]) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pod is restarting frequently"
          description: "Pod {{ $labels.pod }} has restarted {{ $value }} times in the last hour"

      # 数据库连接池耗尽
      - alert: DatabaseConnectionPoolExhausted
        expr: |
          db_pool_available_connections / db_pool_size < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Only {{ $value | humanizePercentage }} connections available"

      # Redis 内存使用
      - alert: RedisHighMemoryUsage
        expr: |
          redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage is high"
          description: "Redis is using {{ $value | humanizePercentage }} of max memory"
```

### 5.4 Grafana Dashboard (JSON)

```json
{
  "dashboard": {
    "title": "Platform API Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (method, path)",
            "legendFormat": "{{method}} {{path}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))",
            "legendFormat": "Error Rate"
          }
        ]
      },
      {
        "title": "Response Time (P50, P90, P99)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.90, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "P90"
          },
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "P99"
          }
        ]
      }
    ]
  }
}
```

---

## 6. 数据库运维

### 6.1 迁移管理

```bash
# 创建迁移
uv run alembic revision --autogenerate -m "add user table"

# 应用迁移
uv run alembic upgrade head

# 回滚一个版本
uv run alembic downgrade -1

# 查看当前版本
uv run alembic current

# 查看迁移历史
uv run alembic history

# 生成 SQL 脚本（用于审核）
uv run alembic upgrade head --sql > migration.sql
```

### 6.2 备份策略

```bash
#!/bin/bash
# scripts/backup-db.sh

set -euo pipefail

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
RETENTION_DAYS=30

# 全量备份
pg_dump -h $DB_HOST -U $DB_USER -d platform \
  --format=custom \
  --file="${BACKUP_DIR}/platform_${DATE}.dump"

# 压缩
gzip "${BACKUP_DIR}/platform_${DATE}.dump"

# 上传到 S3
aws s3 cp "${BACKUP_DIR}/platform_${DATE}.dump.gz" \
  "s3://platform-backups/postgres/"

# 清理旧备份
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# 验证备份
pg_restore --list "${BACKUP_DIR}/platform_${DATE}.dump.gz" > /dev/null
```

### 6.3 只读副本配置

```yaml
# PostgreSQL 主从配置
primary:
  postgresql.conf:
    wal_level: replica
    max_wal_senders: 10
    wal_keep_size: 1GB
    synchronous_commit: on

replica:
  recovery.conf:
    standby_mode: on
    primary_conninfo: "host=primary user=replicator password=xxx"
    trigger_file: /tmp/postgresql.trigger
```

---

## 7. 安全加固

### 7.1 网络策略

```yaml
# deploy/kubernetes/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: platform-api-policy
  namespace: platform
spec:
  podSelector:
    matchLabels:
      app: platform-api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
        - podSelector:
            matchLabels:
              app: platform-api
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
```

### 7.2 Secret 管理

```yaml
# 使用 External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: platform-secrets
  namespace: platform
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: platform-secrets
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: platform/database
        property: url
    - secretKey: JWT_SECRET_KEY
      remoteRef:
        key: platform/jwt
        property: secret
```

### 7.3 安全扫描

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'

jobs:
  trivy:
    name: Container Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t platform-api:scan -f deploy/docker/Dockerfile.api .

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: platform-api:scan
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH

      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: trivy-results.sarif

  dependency-check:
    name: Dependency Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Audit dependencies
        run: uv pip audit
```

---

## 8. 故障排查

### 8.1 常用命令

```bash
# ===== Kubernetes 调试 =====

# 查看 Pod 状态
kubectl get pods -n platform -o wide

# 查看 Pod 详情
kubectl describe pod <pod-name> -n platform

# 查看 Pod 日志
kubectl logs <pod-name> -n platform --tail=100 -f

# 查看前一个容器日志（崩溃恢复场景）
kubectl logs <pod-name> -n platform --previous

# 进入容器
kubectl exec -it <pod-name> -n platform -- /bin/sh

# 端口转发调试
kubectl port-forward svc/platform-api 8000:80 -n platform

# 查看资源使用
kubectl top pods -n platform

# 查看事件
kubectl get events -n platform --sort-by='.lastTimestamp'

# ===== 数据库调试 =====

# 连接数检查
SELECT count(*) FROM pg_stat_activity;

# 慢查询
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

# 锁检查
SELECT * FROM pg_locks WHERE NOT granted;

# ===== Redis 调试 =====

# 内存使用
redis-cli INFO memory

# 慢日志
redis-cli SLOWLOG GET 10

# 客户端连接
redis-cli CLIENT LIST
```

### 8.2 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| Pod CrashLoopBackOff | 应用启动失败 | 检查日志、环境变量、依赖服务 |
| 503 Service Unavailable | Pod 未就绪 | 检查 readiness probe、资源限制 |
| 高延迟 | 数据库慢查询、资源不足 | 检查 DB 索引、增加资源 |
| OOMKilled | 内存不足 | 增加内存限制、检查内存泄漏 |
| Connection Refused | 服务未启动、网络策略 | 检查服务状态、网络策略 |

### 8.3 日志聚合查询 (Loki)

```logql
# 错误日志
{namespace="platform", app="platform-api"} |= "error"

# 特定用户请求
{namespace="platform"} | json | user_id="12345"

# 慢请求 (>1s)
{namespace="platform"} | json | duration_ms > 1000

# 按错误类型统计
sum by (error_code) (
  count_over_time({namespace="platform"} | json | level="error" [5m])
)
```

---

## 9. 运维 Runbook

### 9.1 服务发布

```markdown
## 服务发布检查清单

### 发布前
- [ ] 代码已通过所有测试
- [ ] PR 已获得 2+ 审批
- [ ] 数据库迁移已在 Staging 验证
- [ ] 性能测试通过
- [ ] 发布通知已发送

### 发布中
- [ ] 监控告警静默 (30 min)
- [ ] 触发部署流水线
- [ ] 验证滚动更新状态
- [ ] 检查新 Pod 健康状态
- [ ] 验证关键业务功能

### 发布后
- [ ] 监控错误率 15 分钟
- [ ] 检查 P99 延迟
- [ ] 验证日志无异常
- [ ] 取消告警静默
- [ ] 更新发布日志
```

### 9.2 回滚流程

```bash
#!/bin/bash
# scripts/rollback.sh

set -euo pipefail

NAMESPACE=${1:-platform}
DEPLOYMENT=${2:-platform-api}

echo "Rolling back $DEPLOYMENT in $NAMESPACE..."

# 查看历史版本
kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE

# 回滚到上一版本
kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE

# 等待回滚完成
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=300s

# 验证
kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT

echo "Rollback completed!"
```

### 9.3 扩容流程

```bash
#!/bin/bash
# scripts/scale.sh

NAMESPACE=${1:-platform}
DEPLOYMENT=${2:-platform-api}
REPLICAS=${3:-5}

echo "Scaling $DEPLOYMENT to $REPLICAS replicas..."

kubectl scale deployment/$DEPLOYMENT --replicas=$REPLICAS -n $NAMESPACE

kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE

echo "Scaling completed!"
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-06
**作者**: Platform Architecture Team
