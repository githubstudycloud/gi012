package com.platform.user.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.platform.core.mybatis.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serial;

/**
 * 角色实体
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("t_role")
public class Role extends BaseEntity {

    @Serial
    private static final long serialVersionUID = 1L;

    /**
     * 角色编码
     */
    private String code;

    /**
     * 角色名称
     */
    private String name;

    /**
     * 排序
     */
    private Integer sort;

    /**
     * 状态 (0: 禁用, 1: 正常)
     */
    private Integer status;

    /**
     * 租户ID
     */
    private Long tenantId;

    /**
     * 数据权限范围 (1: 全部, 2: 本部门及以下, 3: 本部门, 4: 仅本人)
     */
    private Integer dataScope;

    /**
     * 备注
     */
    private String remark;
}
