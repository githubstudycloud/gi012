package com.platform.user.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.platform.common.enums.ResultCode;
import com.platform.common.exception.BusinessException;
import com.platform.common.result.PageResult;
import com.platform.user.converter.UserConverter;
import com.platform.user.dto.UserCreateRequest;
import com.platform.user.dto.UserDTO;
import com.platform.user.dto.UserQueryRequest;
import com.platform.user.entity.User;
import com.platform.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;
import java.util.Set;

/**
 * 用户服务
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class UserService extends ServiceImpl<UserMapper, User> {

    private final UserMapper userMapper;
    private final UserConverter userConverter;
    private final PasswordEncoder passwordEncoder;

    /**
     * 分页查询用户
     */
    public PageResult<UserDTO> page(UserQueryRequest request) {
        Page<User> page = new Page<>(request.getPageNum(), request.getPageSize());

        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.hasText(request.getUsername()), User::getUsername, request.getUsername())
                .like(StringUtils.hasText(request.getNickname()), User::getNickname, request.getNickname())
                .like(StringUtils.hasText(request.getMobile()), User::getMobile, request.getMobile())
                .like(StringUtils.hasText(request.getEmail()), User::getEmail, request.getEmail())
                .eq(request.getStatus() != null, User::getStatus, request.getStatus())
                .eq(request.getDeptId() != null, User::getDeptId, request.getDeptId())
                .ge(request.getCreatedAtStart() != null, User::getCreatedAt, request.getCreatedAtStart())
                .le(request.getCreatedAtEnd() != null, User::getCreatedAt, request.getCreatedAtEnd())
                .orderByDesc(User::getCreatedAt);

        Page<User> resultPage = page(page, wrapper);

        List<UserDTO> dtoList = userConverter.toDTOList(resultPage.getRecords());
        return PageResult.of(dtoList, resultPage.getCurrent(), resultPage.getSize(), resultPage.getTotal());
    }

    /**
     * 根据ID获取用户
     */
    public UserDTO getById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw BusinessException.of(ResultCode.USER_NOT_FOUND);
        }
        return userConverter.toDTO(user);
    }

    /**
     * 创建用户
     */
    @Transactional(rollbackFor = Exception.class)
    public Long create(UserCreateRequest request) {
        // 检查用户名是否存在
        if (userMapper.selectByUsername(request.getUsername()) != null) {
            throw BusinessException.of(ResultCode.USER_ALREADY_EXISTS, "用户名已存在");
        }

        // 检查邮箱是否存在
        if (StringUtils.hasText(request.getEmail())
                && userMapper.selectByEmail(request.getEmail()) != null) {
            throw BusinessException.of(ResultCode.USER_ALREADY_EXISTS, "邮箱已被使用");
        }

        // 检查手机号是否存在
        if (StringUtils.hasText(request.getMobile())
                && userMapper.selectByMobile(request.getMobile()) != null) {
            throw BusinessException.of(ResultCode.USER_ALREADY_EXISTS, "手机号已被使用");
        }

        // 创建用户
        User user = userConverter.toEntity(request);
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setStatus(1);

        save(user);

        // TODO: 保存用户角色关联

        log.info("创建用户成功: {}", user.getUsername());
        return user.getId();
    }

    /**
     * 更新用户
     */
    @Transactional(rollbackFor = Exception.class)
    public void update(Long id, UserCreateRequest request) {
        User existing = userMapper.selectById(id);
        if (existing == null) {
            throw BusinessException.of(ResultCode.USER_NOT_FOUND);
        }

        // 检查用户名是否被其他人使用
        User byUsername = userMapper.selectByUsername(request.getUsername());
        if (byUsername != null && !byUsername.getId().equals(id)) {
            throw BusinessException.of(ResultCode.USER_ALREADY_EXISTS, "用户名已存在");
        }

        // 更新用户
        userConverter.updateEntity(request, existing);
        if (StringUtils.hasText(request.getPassword())) {
            existing.setPassword(passwordEncoder.encode(request.getPassword()));
        }

        updateById(existing);

        // TODO: 更新用户角色关联

        log.info("更新用户成功: {}", existing.getUsername());
    }

    /**
     * 删除用户
     */
    @Transactional(rollbackFor = Exception.class)
    public void delete(Long id) {
        User existing = userMapper.selectById(id);
        if (existing == null) {
            throw BusinessException.of(ResultCode.USER_NOT_FOUND);
        }

        removeById(id);

        // TODO: 删除用户角色关联

        log.info("删除用户成功: {}", existing.getUsername());
    }

    /**
     * 批量删除用户
     */
    @Transactional(rollbackFor = Exception.class)
    public void batchDelete(List<Long> ids) {
        removeByIds(ids);
        log.info("批量删除用户成功: {}", ids);
    }

    /**
     * 更新用户状态
     */
    @Transactional(rollbackFor = Exception.class)
    public void updateStatus(Long id, Integer status) {
        User existing = userMapper.selectById(id);
        if (existing == null) {
            throw BusinessException.of(ResultCode.USER_NOT_FOUND);
        }

        existing.setStatus(status);
        updateById(existing);

        log.info("更新用户状态成功: id={}, status={}", id, status);
    }

    /**
     * 重置密码
     */
    @Transactional(rollbackFor = Exception.class)
    public void resetPassword(Long id, String newPassword) {
        User existing = userMapper.selectById(id);
        if (existing == null) {
            throw BusinessException.of(ResultCode.USER_NOT_FOUND);
        }

        existing.setPassword(passwordEncoder.encode(newPassword));
        updateById(existing);

        log.info("重置用户密码成功: {}", existing.getUsername());
    }

    /**
     * 获取用户角色编码列表
     */
    public Set<String> getRoleCodes(Long userId) {
        return userMapper.selectRoleCodesByUserId(userId);
    }

    /**
     * 获取用户权限编码列表
     */
    public Set<String> getPermissionCodes(Long userId) {
        return userMapper.selectPermissionCodesByUserId(userId);
    }
}
