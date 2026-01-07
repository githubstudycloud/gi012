package com.platform.user.dto;

import lombok.Data;

import java.io.Serial;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.Set;

/**
 * 用户 DTO
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Data
public class UserDTO implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    /**
     * 用户ID
     */
    private Long id;

    /**
     * 用户名
     */
    private String username;

    /**
     * 昵称
     */
    private String nickname;

    /**
     * 头像
     */
    private String avatar;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 手机号
     */
    private String mobile;

    /**
     * 性别 (0: 未知, 1: 男, 2: 女)
     */
    private Integer gender;

    /**
     * 状态 (0: 禁用, 1: 正常)
     */
    private Integer status;

    /**
     * 部门ID
     */
    private Long deptId;

    /**
     * 部门名称
     */
    private String deptName;

    /**
     * 角色ID列表
     */
    private Set<Long> roleIds;

    /**
     * 角色名称列表
     */
    private Set<String> roleNames;

    /**
     * 最后登录时间
     */
    private LocalDateTime lastLoginAt;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 备注
     */
    private String remark;
}
