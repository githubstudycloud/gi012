package com.platform.common.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 响应状态码枚举
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Getter
@AllArgsConstructor
public enum ResultCode {

    // ==================== 成功 ====================
    SUCCESS(200, "操作成功"),

    // ==================== 客户端错误 4xx ====================
    BAD_REQUEST(400, "请求参数错误"),
    UNAUTHORIZED(401, "未授权访问"),
    FORBIDDEN(403, "禁止访问"),
    NOT_FOUND(404, "资源不存在"),
    METHOD_NOT_ALLOWED(405, "请求方法不支持"),
    CONFLICT(409, "资源冲突"),
    UNPROCESSABLE_ENTITY(422, "请求参数校验失败"),
    TOO_MANY_REQUESTS(429, "请求过于频繁"),

    // ==================== 服务端错误 5xx ====================
    INTERNAL_SERVER_ERROR(500, "服务器内部错误"),
    SERVICE_UNAVAILABLE(503, "服务暂不可用"),
    GATEWAY_TIMEOUT(504, "网关超时"),

    // ==================== 业务错误 1xxx ====================
    // 用户模块 10xx
    USER_NOT_FOUND(1001, "用户不存在"),
    USER_PASSWORD_ERROR(1002, "用户名或密码错误"),
    USER_DISABLED(1003, "用户已被禁用"),
    USER_ALREADY_EXISTS(1004, "用户已存在"),
    USER_TOKEN_EXPIRED(1005, "登录已过期，请重新登录"),
    USER_TOKEN_INVALID(1006, "无效的Token"),

    // 权限模块 11xx
    PERMISSION_DENIED(1101, "权限不足"),
    ROLE_NOT_FOUND(1102, "角色不存在"),

    // 文件模块 12xx
    FILE_NOT_FOUND(1201, "文件不存在"),
    FILE_UPLOAD_FAILED(1202, "文件上传失败"),
    FILE_TYPE_NOT_ALLOWED(1203, "文件类型不允许"),
    FILE_SIZE_EXCEEDED(1204, "文件大小超出限制"),

    // 数据模块 13xx
    DATA_NOT_FOUND(1301, "数据不存在"),
    DATA_ALREADY_EXISTS(1302, "数据已存在"),
    DATA_INTEGRITY_VIOLATION(1303, "数据完整性约束冲突");

    /**
     * 状态码
     */
    private final int code;

    /**
     * 描述信息
     */
    private final String message;
}
