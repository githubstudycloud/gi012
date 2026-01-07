package com.platform.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.platform.user.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.Set;

/**
 * 用户 Mapper
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {

    /**
     * 根据用户名查询用户
     */
    @Select("SELECT * FROM t_user WHERE username = #{username} AND deleted = 0")
    User selectByUsername(@Param("username") String username);

    /**
     * 根据邮箱查询用户
     */
    @Select("SELECT * FROM t_user WHERE email = #{email} AND deleted = 0")
    User selectByEmail(@Param("email") String email);

    /**
     * 根据手机号查询用户
     */
    @Select("SELECT * FROM t_user WHERE mobile = #{mobile} AND deleted = 0")
    User selectByMobile(@Param("mobile") String mobile);

    /**
     * 查询用户的角色编码列表
     */
    @Select("""
            SELECT r.code FROM t_role r
            INNER JOIN t_user_role ur ON r.id = ur.role_id
            WHERE ur.user_id = #{userId} AND r.deleted = 0 AND r.status = 1
            """)
    Set<String> selectRoleCodesByUserId(@Param("userId") Long userId);

    /**
     * 查询用户的权限编码列表
     */
    @Select("""
            SELECT DISTINCT p.code FROM t_permission p
            INNER JOIN t_role_permission rp ON p.id = rp.permission_id
            INNER JOIN t_user_role ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = #{userId} AND p.deleted = 0 AND p.status = 1
            """)
    Set<String> selectPermissionCodesByUserId(@Param("userId") Long userId);
}
