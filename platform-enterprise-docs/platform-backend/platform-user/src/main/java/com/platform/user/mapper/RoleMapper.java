package com.platform.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.platform.user.entity.Role;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 角色 Mapper
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Mapper
public interface RoleMapper extends BaseMapper<Role> {

    /**
     * 根据角色编码查询角色
     */
    @Select("SELECT * FROM t_role WHERE code = #{code} AND deleted = 0")
    Role selectByCode(@Param("code") String code);

    /**
     * 查询用户的角色列表
     */
    @Select("""
            SELECT r.* FROM t_role r
            INNER JOIN t_user_role ur ON r.id = ur.role_id
            WHERE ur.user_id = #{userId} AND r.deleted = 0
            """)
    List<Role> selectByUserId(@Param("userId") Long userId);
}
