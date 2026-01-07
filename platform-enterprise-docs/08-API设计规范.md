# Platform Enterprise - API 设计规范

> RESTful API 设计标准与最佳实践

## 1. 设计原则

### 1.1 REST 成熟度模型

```
Level 3: HATEOAS (超媒体即应用状态引擎)
    ↑
Level 2: HTTP 动词 (GET, POST, PUT, DELETE)
    ↑
Level 1: 资源 (URI 标识资源)
    ↑
Level 0: HTTP 作为传输层
```

**目标**: 达到 Level 2，关键资源支持 Level 3

### 1.2 核心原则

| 原则 | 描述 |
|------|------|
| 资源导向 | URI 表示资源，而非操作 |
| 统一接口 | 使用标准 HTTP 方法 |
| 无状态 | 请求包含所有必要信息 |
| 可缓存 | 合理使用缓存头 |
| 分层系统 | 客户端无需知道后端结构 |

## 2. URI 设计

### 2.1 命名规范

```yaml
# 基础格式
pattern: "/api/{version}/{resource}"

# 规则
rules:
  - 使用小写字母
  - 使用连字符分隔单词 (kebab-case)
  - 使用名词复数表示集合
  - 避免动词 (除非是非 CRUD 操作)
  - 不超过 3 层嵌套

# 正确示例
good:
  - GET    /api/v1/users                    # 获取用户列表
  - GET    /api/v1/users/123                # 获取单个用户
  - POST   /api/v1/users                    # 创建用户
  - PUT    /api/v1/users/123                # 更新用户
  - DELETE /api/v1/users/123                # 删除用户
  - GET    /api/v1/users/123/roles          # 获取用户的角色
  - POST   /api/v1/users/123/roles          # 为用户分配角色
  - POST   /api/v1/auth/login               # 登录 (非 CRUD 操作)
  - POST   /api/v1/orders/123/cancel        # 取消订单 (状态变更)

# 错误示例
bad:
  - GET    /api/v1/getUsers                 # 不要用动词
  - GET    /api/v1/user                     # 集合用复数
  - POST   /api/v1/users/create             # 不要重复动词
  - GET    /api/v1/users/123/roles/456/permissions  # 嵌套过深
```

### 2.2 版本控制

```yaml
# 推荐方式: URI 路径版本
preferred:
  - /api/v1/users
  - /api/v2/users

# 备选方式: 请求头版本
alternative:
  header: "Accept: application/vnd.platform.v1+json"

# 版本策略
strategy:
  - 新版本发布后，旧版本至少维护 12 个月
  - 弃用 API 需要提前 3 个月通知
  - 使用 Sunset 响应头标识弃用时间
```

## 3. HTTP 方法

### 3.1 方法语义

| 方法 | 语义 | 幂等 | 安全 | 请求体 | 响应体 |
|------|------|------|------|--------|--------|
| GET | 获取资源 | ✅ | ✅ | ❌ | ✅ |
| POST | 创建资源 | ❌ | ❌ | ✅ | ✅ |
| PUT | 替换资源 | ✅ | ❌ | ✅ | ✅ |
| PATCH | 部分更新 | ❌ | ❌ | ✅ | ✅ |
| DELETE | 删除资源 | ✅ | ❌ | ❌ | ❌/✅ |
| HEAD | 获取元数据 | ✅ | ✅ | ❌ | ❌ |
| OPTIONS | 获取支持的方法 | ✅ | ✅ | ❌ | ✅ |

### 3.2 使用场景

```java
// GET - 获取资源
@GetMapping("/users")
public PageResponse<UserDTO> listUsers(
    @RequestParam(defaultValue = "1") int page,
    @RequestParam(defaultValue = "10") int size
) { }

@GetMapping("/users/{id}")
public UserDTO getUser(@PathVariable Long id) { }

// POST - 创建资源
@PostMapping("/users")
@ResponseStatus(HttpStatus.CREATED)
public UserDTO createUser(@Valid @RequestBody CreateUserRequest request) { }

// PUT - 完整更新 (需要提供所有字段)
@PutMapping("/users/{id}")
public UserDTO updateUser(
    @PathVariable Long id,
    @Valid @RequestBody UpdateUserRequest request
) { }

// PATCH - 部分更新 (只更新提供的字段)
@PatchMapping("/users/{id}")
public UserDTO patchUser(
    @PathVariable Long id,
    @RequestBody Map<String, Object> updates
) { }

// DELETE - 删除资源
@DeleteMapping("/users/{id}")
@ResponseStatus(HttpStatus.NO_CONTENT)
public void deleteUser(@PathVariable Long id) { }
```

## 4. 请求与响应

### 4.1 请求格式

```typescript
// 查询参数 (GET 请求)
GET /api/v1/users?page=1&size=10&sort=createdAt,desc&status=ACTIVE

// 路径参数
GET /api/v1/users/123

// 请求体 (POST/PUT/PATCH)
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecureP@ss123",
  "roles": ["USER", "ADMIN"]
}
```

### 4.2 统一响应格式

```typescript
// 成功响应
interface ApiResponse<T> {
  code: number          // 业务状态码
  message: string       // 状态描述
  data: T              // 响应数据
  timestamp: number    // 时间戳
}

// 成功示例
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "timestamp": 1704499200000
}

// 分页响应
interface PageResponse<T> {
  code: number
  message: string
  data: {
    items: T[]          // 数据列表
    total: number       // 总记录数
    page: number        // 当前页码
    size: number        // 每页大小
    totalPages: number  // 总页数
  }
  timestamp: number
}

// 分页示例
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      { "id": 1, "username": "john" },
      { "id": 2, "username": "jane" }
    ],
    "total": 100,
    "page": 1,
    "size": 10,
    "totalPages": 10
  },
  "timestamp": 1704499200000
}
```

### 4.3 错误响应

```typescript
// 错误响应格式
interface ErrorResponse {
  code: number          // 错误码
  message: string       // 错误信息
  details?: string      // 详细描述 (开发环境)
  path?: string         // 请求路径
  timestamp: number     // 时间戳
  errors?: FieldError[] // 字段错误 (验证失败时)
}

interface FieldError {
  field: string         // 字段名
  message: string       // 错误描述
  rejectedValue?: any   // 被拒绝的值
}

// 验证错误示例
{
  "code": 400,
  "message": "请求参数验证失败",
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确",
      "rejectedValue": "invalid-email"
    },
    {
      "field": "password",
      "message": "密码长度必须在 6-100 字符之间"
    }
  ],
  "timestamp": 1704499200000
}
```

## 5. HTTP 状态码

### 5.1 状态码映射

```yaml
# 2xx 成功
200 OK:
  - GET 成功获取资源
  - PUT/PATCH 成功更新资源
  - POST 执行操作成功 (非创建)

201 Created:
  - POST 成功创建资源
  - 应返回 Location 头指向新资源

204 No Content:
  - DELETE 成功删除资源
  - 无响应体

# 3xx 重定向
301 Moved Permanently:  资源永久移动
302 Found:              临时重定向
304 Not Modified:       资源未修改 (缓存)

# 4xx 客户端错误
400 Bad Request:        请求格式错误、参数验证失败
401 Unauthorized:       未认证
403 Forbidden:          已认证但无权限
404 Not Found:          资源不存在
405 Method Not Allowed: HTTP 方法不支持
409 Conflict:           资源冲突 (如重复创建)
422 Unprocessable Entity: 语义错误
429 Too Many Requests:  请求频率限制

# 5xx 服务端错误
500 Internal Server Error: 服务器内部错误
502 Bad Gateway:           网关错误
503 Service Unavailable:   服务不可用
504 Gateway Timeout:       网关超时
```

### 5.2 错误码设计

```java
public enum ErrorCode {
    // 通用错误 (1000-1999)
    SUCCESS(200, "操作成功"),
    BAD_REQUEST(400, "请求参数错误"),
    UNAUTHORIZED(401, "未授权"),
    FORBIDDEN(403, "禁止访问"),
    NOT_FOUND(404, "资源不存在"),
    INTERNAL_ERROR(500, "服务器内部错误"),

    // 认证错误 (2000-2999)
    AUTH_TOKEN_INVALID(2001, "令牌无效"),
    AUTH_TOKEN_EXPIRED(2002, "令牌已过期"),
    AUTH_LOGIN_FAILED(2003, "用户名或密码错误"),
    AUTH_ACCOUNT_LOCKED(2004, "账户已锁定"),
    AUTH_CAPTCHA_ERROR(2005, "验证码错误"),

    // 用户错误 (3000-3999)
    USER_NOT_FOUND(3001, "用户不存在"),
    USER_ALREADY_EXISTS(3002, "用户已存在"),
    USER_DISABLED(3003, "用户已禁用"),
    USER_PASSWORD_ERROR(3004, "密码错误"),

    // 业务错误 (4000-4999)
    ORDER_NOT_FOUND(4001, "订单不存在"),
    ORDER_STATUS_ERROR(4002, "订单状态异常"),
    INVENTORY_NOT_ENOUGH(4003, "库存不足"),

    // 文件错误 (5000-5999)
    FILE_NOT_FOUND(5001, "文件不存在"),
    FILE_TYPE_NOT_ALLOWED(5002, "文件类型不允许"),
    FILE_SIZE_EXCEEDED(5003, "文件大小超出限制");

    private final int code;
    private final String message;
}
```

## 6. 过滤、排序、分页

### 6.1 查询参数规范

```yaml
# 分页
pagination:
  page: 1              # 页码 (从 1 开始)
  size: 10             # 每页大小 (最大 100)
  example: "?page=1&size=20"

# 排序
sorting:
  sort: "field,direction"  # 字段,方向
  direction: [asc, desc]
  multiple: true           # 支持多字段排序
  example: "?sort=createdAt,desc&sort=name,asc"

# 过滤
filtering:
  exact: "?status=ACTIVE"
  like: "?username=*john*"
  range: "?createdAt.gte=2024-01-01&createdAt.lte=2024-12-31"
  in: "?status.in=ACTIVE,INACTIVE"
  null: "?email.null=true"

# 字段选择
fields:
  include: "?fields=id,username,email"
  exclude: "?fields.exclude=password,secret"

# 关联加载
expand:
  example: "?expand=roles,department"
```

### 6.2 实现示例

```java
// 查询参数对象
public record UserQueryRequest(
    @Min(1) Integer page,
    @Min(1) @Max(100) Integer size,
    String sort,
    String keyword,
    UserStatus status,
    LocalDate createdAtStart,
    LocalDate createdAtEnd
) {
    public UserQueryRequest {
        if (page == null) page = 1;
        if (size == null) size = 10;
    }

    public Pageable toPageable() {
        Sort sortSpec = Sort.unsorted();
        if (sort != null) {
            String[] parts = sort.split(",");
            Sort.Direction direction = parts.length > 1 && "desc".equalsIgnoreCase(parts[1])
                ? Sort.Direction.DESC : Sort.Direction.ASC;
            sortSpec = Sort.by(direction, parts[0]);
        }
        return PageRequest.of(page - 1, size, sortSpec);
    }
}

// 控制器
@GetMapping("/users")
public PageResponse<UserDTO> listUsers(@Valid UserQueryRequest request) {
    return userService.search(request);
}
```

## 7. API 文档

### 7.1 OpenAPI 3.0 注解

```java
@RestController
@RequestMapping("/api/v1/users")
@Tag(name = "用户管理", description = "用户的增删改查操作")
public class UserController {

    @Operation(
        summary = "获取用户列表",
        description = "分页获取用户列表，支持条件筛选"
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "获取成功"),
        @ApiResponse(responseCode = "401", description = "未授权"),
        @ApiResponse(responseCode = "500", description = "服务器错误")
    })
    @GetMapping
    public PageResponse<UserDTO> listUsers(
        @Parameter(description = "页码", example = "1")
        @RequestParam(defaultValue = "1") int page,

        @Parameter(description = "每页大小", example = "10")
        @RequestParam(defaultValue = "10") int size,

        @Parameter(description = "关键词搜索")
        @RequestParam(required = false) String keyword
    ) {
        return userService.list(page, size, keyword);
    }

    @Operation(summary = "创建用户")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "创建成功"),
        @ApiResponse(responseCode = "400", description = "参数验证失败"),
        @ApiResponse(responseCode = "409", description = "用户已存在")
    })
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserDTO createUser(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(
            description = "用户信息",
            required = true,
            content = @Content(schema = @Schema(implementation = CreateUserRequest.class))
        )
        @Valid @RequestBody CreateUserRequest request
    ) {
        return userService.create(request);
    }
}
```

### 7.2 DTO 文档注解

```java
@Schema(description = "创建用户请求")
public record CreateUserRequest(
    @Schema(description = "用户名", example = "john_doe", minLength = 4, maxLength = 50)
    @NotBlank
    @Size(min = 4, max = 50)
    String username,

    @Schema(description = "密码", example = "P@ssw0rd123", minLength = 6, maxLength = 100)
    @NotBlank
    @Size(min = 6, max = 100)
    String password,

    @Schema(description = "邮箱", example = "john@example.com")
    @Email
    String email,

    @Schema(description = "昵称", example = "John Doe")
    String nickname,

    @Schema(description = "角色列表", example = "[\"USER\", \"ADMIN\"]")
    List<String> roles
) {}
```

## 8. 安全规范

### 8.1 认证与授权

```yaml
# 认证方式
authentication:
  type: Bearer Token (JWT)
  header: "Authorization: Bearer {token}"

# 需要认证的 API
secured:
  - /api/v1/users/**
  - /api/v1/orders/**

# 公开 API
public:
  - /api/v1/auth/login
  - /api/v1/auth/register
  - /api/v1/public/**
```

### 8.2 请求限流

```yaml
# 默认限流
default:
  rate: 100/s
  burst: 200

# 敏感接口限流
sensitive:
  /api/v1/auth/login:
    rate: 5/min
    burst: 10
  /api/v1/auth/register:
    rate: 3/min
    burst: 5

# 响应头
headers:
  X-RateLimit-Limit: 100      # 限制
  X-RateLimit-Remaining: 95   # 剩余
  X-RateLimit-Reset: 1704499260  # 重置时间
```

### 8.3 请求签名 (可选)

```yaml
# 高安全场景下的请求签名
signature:
  algorithm: HMAC-SHA256
  headers:
    - X-Timestamp: 请求时间戳
    - X-Nonce: 随机字符串
    - X-Signature: 签名值

  # 签名计算
  formula: |
    stringToSign = method + "\n" +
                   path + "\n" +
                   timestamp + "\n" +
                   nonce + "\n" +
                   body_hash
    signature = HMAC-SHA256(secretKey, stringToSign)
```

## 9. 最佳实践

### 9.1 API 设计清单

```yaml
checklist:
  uri:
    - [ ] URI 使用名词复数
    - [ ] URI 使用小写和连字符
    - [ ] 嵌套不超过 3 层
    - [ ] 包含版本号

  method:
    - [ ] GET 不修改数据
    - [ ] POST 用于创建
    - [ ] PUT 用于完整更新
    - [ ] PATCH 用于部分更新
    - [ ] DELETE 用于删除

  response:
    - [ ] 统一响应格式
    - [ ] 正确的 HTTP 状态码
    - [ ] 有意义的错误信息
    - [ ] 分页响应包含元数据

  security:
    - [ ] 需要认证的 API 已保护
    - [ ] 敏感操作需要授权
    - [ ] 输入已验证
    - [ ] 敏感数据已脱敏

  documentation:
    - [ ] 所有 API 有文档
    - [ ] 请求/响应示例完整
    - [ ] 错误码已列出
```

### 9.2 版本迁移策略

```yaml
migration:
  # 1. 发布新版本
  - announce: "v2 API 即将发布"
    date: "2026-01-01"

  # 2. 新旧版本并行
  - parallel:
      v1: "/api/v1/*"
      v2: "/api/v2/*"
    duration: "6 months"

  # 3. 弃用旧版本
  - deprecate:
      version: v1
      header: "Sunset: Sat, 01 Jul 2026 00:00:00 GMT"
      warning: "Deprecation: API v1 will be removed on 2026-07-01"

  # 4. 移除旧版本
  - remove:
      version: v1
      date: "2026-07-01"
```

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-06
