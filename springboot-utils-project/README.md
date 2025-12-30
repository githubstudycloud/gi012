# SpringBoot 工具类项目

## 项目介绍

基于 SpringBoot 2.7.18 的实用工具类项目，兼容 JDK8，提供了 IP 工具、缓存管理、请求链路追踪、系统信息获取等常用功能。

## 技术栈

- SpringBoot 2.7.18
- JDK 1.8
- Caffeine 2.9.3 (本地缓存)
- Maven

## 工具类清单

### 1. IpUtil - IP地址工具类
提供IP地址相关的常用操作，包括：
- 获取客户端真实IP（支持代理、负载均衡）
- IPv4地址格式验证
- IP地址与长整型互转
- 判断内网IP/回环地址
- 获取本机IP地址
- 获取IP所在网段
- 判断IP是否在指定网段内

**代码量**: 约280行

### 2. CacheManager - 本地缓存管理器
基于Caffeine实现的高性能本地缓存，包括：
- 创建和获取缓存实例
- 缓存的增删改查操作
- 缓存统计信息（命中率、淘汰次数等）
- 支持自定义过期时间和最大容量
- 批量操作支持

**代码量**: 约300行

### 3. TraceLogUtil - 请求链路追踪工具
用于生成和管理TraceID，实现分布式请求链路追踪：
- 生成TraceID和SpanID
- 支持父子链路追踪
- MDC集成，自动附加到日志
- 计算请求耗时
- TraceContext快照和恢复
- 业务日志自动附加TraceID

**代码量**: 约350行

### 4. SystemInfoUtil - 系统信息获取工具
获取系统CPU、内存、磁盘、JVM等信息：
- CPU核心数、系统/进程CPU负载
- 系统内存总量、已用、空闲、使用率
- JVM内存信息、运行时长
- 磁盘空间信息
- 操作系统信息
- 线程统计、类加载统计
- 格式化工具（字节、时长）

**代码量**: 约380行

## 代码规范

- ✅ 不catch大异常（Exception、RuntimeException、Throwable）
- ✅ 代码嵌套不超过4层
- ✅ 单个方法不超过50行
- ✅ 最小化外部依赖

## 项目结构

```
springboot-utils-project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           └── utils/
│   │   │               ├── controller/
│   │   │               │   └── TestController.java
│   │   │               ├── CacheManager.java
│   │   │               ├── IpUtil.java
│   │   │               ├── SystemInfoUtil.java
│   │   │               ├── TraceLogUtil.java
│   │   │               └── UtilsApplication.java
│   │   └── resources/
│   │       └── application.yml
│   └── test/
└── pom.xml
```

## 快速开始

### 1. 构建项目

```bash
cd springboot-utils-project
mvn clean compile
```

### 2. 启动项目

```bash
mvn spring-boot:run
```

项目将在 `http://localhost:8080` 启动

### 3. 测试接口

#### 健康检查
```bash
curl http://localhost:8080/api/test/health
```

#### 首页（查看所有可用API）
```bash
curl http://localhost:8080/api/test/
```

#### IP工具测试
```bash
curl http://localhost:8080/api/test/ip
```

#### 缓存工具测试
```bash
curl "http://localhost:8080/api/test/cache?key=mykey&value=myvalue"
```

#### 缓存统计
```bash
curl http://localhost:8080/api/test/cache/stats
```

#### 链路追踪测试
```bash
curl http://localhost:8080/api/test/trace
```

#### 系统信息
```bash
# 完整系统信息
curl http://localhost:8080/api/test/system

# CPU信息
curl http://localhost:8080/api/test/system/cpu

# 内存信息
curl http://localhost:8080/api/test/system/memory

# JVM信息
curl http://localhost:8080/api/test/system/jvm
```

## API说明

### 1. IP工具API - `/api/test/ip`
返回IP相关信息，包括真实IP、本机IP、IP验证等

### 2. 缓存API - `/api/test/cache`
- 参数: key, value
- 功能: 测试缓存存取、统计信息

### 3. 链路追踪API - `/api/test/trace`
返回TraceID、SpanID、耗时等链路追踪信息

### 4. 系统信息API
- `/api/test/system` - 完整系统信息
- `/api/test/system/cpu` - CPU信息
- `/api/test/system/memory` - 内存信息
- `/api/test/system/jvm` - JVM信息

## 使用示例

### 在代码中使用工具类

```java
// 1. 使用IP工具
String realIp = IpUtil.getRealIp(request);
boolean isInternal = IpUtil.isInternalIp(realIp);

// 2. 使用缓存管理
CacheManager.put("user:123", userObject);
Object user = CacheManager.get("user:123");
double hitRate = CacheManager.getHitRate();

// 3. 使用链路追踪
String traceId = TraceLogUtil.startTrace();
TraceLogUtil.logInfo("处理业务逻辑");
long duration = TraceLogUtil.endTrace();

// 4. 使用系统信息
int cpuCores = SystemInfoUtil.getCpuCoreCount();
long usedMemory = SystemInfoUtil.getUsedMemoryMB();
Map<String, Object> fullInfo = SystemInfoUtil.getFullSystemInfo();
```

## 统计信息

- **总代码行数**: 1655行
- **工具类数量**: 4个
- **测试接口数量**: 9个
- **依赖包数量**: 3个（SpringBoot Web、Caffeine、Lombok）

## 开发信息

- **作者**: system
- **创建日期**: 2025-12-30
- **版本**: 1.0.0
- **许可**: MIT

## 注意事项

1. 本项目所有工具类都是静态方法，可以直接调用
2. CacheManager使用Caffeine作为本地缓存，适合单机场景
3. TraceLogUtil使用ThreadLocal存储链路信息，注意线程池场景下的使用
4. SystemInfoUtil获取的CPU负载等信息可能在某些环境下不准确
