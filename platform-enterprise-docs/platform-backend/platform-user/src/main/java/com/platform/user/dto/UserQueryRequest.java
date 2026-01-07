package com.platform.user.dto;

import lombok.Data;

import java.io.Serial;
import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 用户查询请求
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Data
public class UserQueryRequest implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    /**
     * 页码
     */
    private Integer pageNum = 1;

    /**
     * 每页大小
     */
    private Integer pageSize = 10;

    /**
     * 用户名（模糊查询）
     */
    private String username;

    /**
     * 昵称（模糊查询）
     */
    private String nickname;

    /**
     * 手机号（模糊查询）
     */
    private String mobile;

    /**
     * 邮箱（模糊查询）
     */
    private String email;

    /**
     * 状态
     */
    private Integer status;

    /**
     * 部门ID
     */
    private Long deptId;

    /**
     * 创建时间开始
     */
    private LocalDateTime createdAtStart;

    /**
     * 创建时间结束
     */
    private LocalDateTime createdAtEnd;
}
