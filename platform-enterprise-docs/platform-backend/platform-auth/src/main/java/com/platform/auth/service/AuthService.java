package com.platform.auth.service;

import com.platform.auth.dto.LoginRequest;
import com.platform.auth.dto.LoginResponse;
import com.platform.auth.dto.RegisterRequest;
import com.platform.common.enums.ResultCode;
import com.platform.common.exception.BusinessException;
import com.platform.core.security.JwtUtils;
import com.platform.core.security.LoginUser;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.TimeUnit;

/**
 * 认证服务
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final JwtUtils jwtUtils;
    private final PasswordEncoder passwordEncoder;
    private final RedisTemplate<String, Object> redisTemplate;

    private static final String TOKEN_BLACKLIST_PREFIX = "platform:token:blacklist:";
    private static final String USER_TOKEN_PREFIX = "platform:user:token:";

    /**
     * 用户登录
     */
    public LoginResponse login(LoginRequest request) {
        // TODO: 从数据库查询用户信息
        // 这里模拟一个用户
        if (!"admin".equals(request.getUsername())) {
            throw BusinessException.of(ResultCode.USER_NOT_FOUND);
        }

        // 验证密码 (模拟密码为 admin123)
        String encodedPassword = passwordEncoder.encode("admin123");
        if (!passwordEncoder.matches(request.getPassword(), encodedPassword)
                && !"admin123".equals(request.getPassword())) {
            throw BusinessException.of(ResultCode.USER_PASSWORD_ERROR);
        }

        // 构建登录用户信息
        LoginUser loginUser = new LoginUser();
        loginUser.setUserId(1L);
        loginUser.setUsername("admin");
        loginUser.setNickname("管理员");
        loginUser.setAvatar("/avatar/default.png");
        loginUser.setEmail("admin@platform.com");
        loginUser.setTenantId(1L);

        Set<String> roles = new HashSet<>();
        roles.add("ADMIN");
        loginUser.setRoles(roles);

        Set<String> permissions = new HashSet<>();
        permissions.add("system:user:list");
        permissions.add("system:user:add");
        permissions.add("system:user:edit");
        permissions.add("system:user:delete");
        permissions.add("system:role:list");
        loginUser.setPermissions(permissions);

        // 生成 Token
        String accessToken = jwtUtils.generateAccessToken(loginUser);
        String refreshToken = jwtUtils.generateRefreshToken(loginUser);

        // 缓存 Token
        String userTokenKey = USER_TOKEN_PREFIX + loginUser.getUserId();
        redisTemplate.opsForValue().set(userTokenKey, accessToken, 7, TimeUnit.DAYS);

        log.info("用户登录成功: {}", loginUser.getUsername());

        return LoginResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .expiresIn(86400L)
                .userId(loginUser.getUserId())
                .username(loginUser.getUsername())
                .nickname(loginUser.getNickname())
                .avatar(loginUser.getAvatar())
                .roles(loginUser.getRoles())
                .permissions(loginUser.getPermissions())
                .build();
    }

    /**
     * 用户注册
     */
    public void register(RegisterRequest request) {
        // 验证密码一致性
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw BusinessException.of(ResultCode.BAD_REQUEST, "两次输入的密码不一致");
        }

        // TODO: 验证验证码
        // TODO: 检查用户名是否已存在
        // TODO: 检查邮箱/手机号是否已存在
        // TODO: 保存用户到数据库

        log.info("用户注册成功: {}", request.getUsername());
    }

    /**
     * 刷新令牌
     */
    public LoginResponse refreshToken(String refreshToken) {
        // 验证刷新令牌
        if (!jwtUtils.validateToken(refreshToken) || !jwtUtils.isRefreshToken(refreshToken)) {
            throw BusinessException.of(ResultCode.USER_TOKEN_INVALID);
        }

        Long userId = jwtUtils.getUserIdFromToken(refreshToken);
        String username = jwtUtils.getUsernameFromToken(refreshToken);

        // TODO: 从数据库重新查询用户信息
        LoginUser loginUser = new LoginUser();
        loginUser.setUserId(userId);
        loginUser.setUsername(username);
        loginUser.setNickname("管理员");
        loginUser.setTenantId(1L);
        loginUser.setRoles(Set.of("ADMIN"));
        loginUser.setPermissions(Set.of("system:user:list"));

        // 生成新的 Token
        String newAccessToken = jwtUtils.generateAccessToken(loginUser);
        String newRefreshToken = jwtUtils.generateRefreshToken(loginUser);

        log.info("刷新令牌成功: {}", username);

        return LoginResponse.builder()
                .accessToken(newAccessToken)
                .refreshToken(newRefreshToken)
                .expiresIn(86400L)
                .userId(loginUser.getUserId())
                .username(loginUser.getUsername())
                .nickname(loginUser.getNickname())
                .roles(loginUser.getRoles())
                .permissions(loginUser.getPermissions())
                .build();
    }

    /**
     * 用户登出
     */
    public void logout(String token) {
        if (jwtUtils.validateToken(token)) {
            Long userId = jwtUtils.getUserIdFromToken(token);
            long remainingTime = jwtUtils.getTokenRemainingTime(token);

            // 将 Token 加入黑名单
            String blacklistKey = TOKEN_BLACKLIST_PREFIX + token;
            redisTemplate.opsForValue().set(blacklistKey, true, remainingTime, TimeUnit.MILLISECONDS);

            // 删除用户 Token 缓存
            String userTokenKey = USER_TOKEN_PREFIX + userId;
            redisTemplate.delete(userTokenKey);

            log.info("用户登出成功: userId={}", userId);
        }
    }

    /**
     * 检查 Token 是否在黑名单中
     */
    public boolean isTokenBlacklisted(String token) {
        String blacklistKey = TOKEN_BLACKLIST_PREFIX + token;
        return Boolean.TRUE.equals(redisTemplate.hasKey(blacklistKey));
    }
}
