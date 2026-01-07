package com.platform.common.constant;

/**
 * 通用常量定义
 *
 * @author Platform Team
 * @since 1.0.0
 */
public final class CommonConstant {

    private CommonConstant() {
        throw new UnsupportedOperationException("常量类不允许实例化");
    }

    // ==================== 系统常量 ====================

    /** 默认页码 */
    public static final int DEFAULT_PAGE_NUM = 1;

    /** 默认每页大小 */
    public static final int DEFAULT_PAGE_SIZE = 10;

    /** 最大每页大小 */
    public static final int MAX_PAGE_SIZE = 100;

    // ==================== 状态常量 ====================

    /** 正常状态 */
    public static final int STATUS_NORMAL = 1;

    /** 禁用状态 */
    public static final int STATUS_DISABLED = 0;

    /** 删除标记 - 未删除 */
    public static final int NOT_DELETED = 0;

    /** 删除标记 - 已删除 */
    public static final int DELETED = 1;

    // ==================== 请求头常量 ====================

    /** 认证请求头 */
    public static final String HEADER_AUTHORIZATION = "Authorization";

    /** Bearer 前缀 */
    public static final String BEARER_PREFIX = "Bearer ";

    /** 用户ID请求头 */
    public static final String HEADER_USER_ID = "X-User-Id";

    /** 用户名请求头 */
    public static final String HEADER_USERNAME = "X-Username";

    /** 租户ID请求头 */
    public static final String HEADER_TENANT_ID = "X-Tenant-Id";

    /** 请求ID请求头 */
    public static final String HEADER_REQUEST_ID = "X-Request-Id";

    // ==================== 缓存相关 ====================

    /** 缓存前缀 */
    public static final String CACHE_PREFIX = "platform:";

    /** 用户缓存前缀 */
    public static final String CACHE_USER_PREFIX = CACHE_PREFIX + "user:";

    /** 权限缓存前缀 */
    public static final String CACHE_PERMISSION_PREFIX = CACHE_PREFIX + "permission:";

    /** Token 缓存前缀 */
    public static final String CACHE_TOKEN_PREFIX = CACHE_PREFIX + "token:";

    // ==================== 时间常量 ====================

    /** 一分钟（秒） */
    public static final int ONE_MINUTE_SECONDS = 60;

    /** 一小时（秒） */
    public static final int ONE_HOUR_SECONDS = 3600;

    /** 一天（秒） */
    public static final int ONE_DAY_SECONDS = 86400;

    /** 一周（秒） */
    public static final int ONE_WEEK_SECONDS = 604800;
}
