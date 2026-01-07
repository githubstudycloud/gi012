package com.platform.user.controller;

import com.platform.common.result.PageResult;
import com.platform.common.result.Result;
import com.platform.user.dto.UserCreateRequest;
import com.platform.user.dto.UserDTO;
import com.platform.user.dto.UserQueryRequest;
import com.platform.user.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 用户管理控制器
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Tag(name = "用户管理", description = "用户CRUD操作")
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "分页查询用户")
    @GetMapping
    @PreAuthorize("hasAuthority('system:user:list')")
    public PageResult<UserDTO> page(UserQueryRequest request) {
        return userService.page(request);
    }

    @Operation(summary = "获取用户详情")
    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('system:user:list')")
    public Result<UserDTO> getById(@Parameter(description = "用户ID") @PathVariable Long id) {
        UserDTO dto = userService.getById(id);
        return Result.success(dto);
    }

    @Operation(summary = "创建用户")
    @PostMapping
    @PreAuthorize("hasAuthority('system:user:add')")
    public Result<Long> create(@Valid @RequestBody UserCreateRequest request) {
        Long id = userService.create(request);
        return Result.success(id);
    }

    @Operation(summary = "更新用户")
    @PutMapping("/{id}")
    @PreAuthorize("hasAuthority('system:user:edit')")
    public Result<Void> update(
            @Parameter(description = "用户ID") @PathVariable Long id,
            @Valid @RequestBody UserCreateRequest request) {
        userService.update(id, request);
        return Result.success();
    }

    @Operation(summary = "删除用户")
    @DeleteMapping("/{id}")
    @PreAuthorize("hasAuthority('system:user:delete')")
    public Result<Void> delete(@Parameter(description = "用户ID") @PathVariable Long id) {
        userService.delete(id);
        return Result.success();
    }

    @Operation(summary = "批量删除用户")
    @DeleteMapping("/batch")
    @PreAuthorize("hasAuthority('system:user:delete')")
    public Result<Void> batchDelete(@RequestBody List<Long> ids) {
        userService.batchDelete(ids);
        return Result.success();
    }

    @Operation(summary = "更新用户状态")
    @PatchMapping("/{id}/status")
    @PreAuthorize("hasAuthority('system:user:edit')")
    public Result<Void> updateStatus(
            @Parameter(description = "用户ID") @PathVariable Long id,
            @Parameter(description = "状态") @RequestParam Integer status) {
        userService.updateStatus(id, status);
        return Result.success();
    }

    @Operation(summary = "重置用户密码")
    @PatchMapping("/{id}/password")
    @PreAuthorize("hasAuthority('system:user:edit')")
    public Result<Void> resetPassword(
            @Parameter(description = "用户ID") @PathVariable Long id,
            @Parameter(description = "新密码") @RequestParam String newPassword) {
        userService.resetPassword(id, newPassword);
        return Result.success();
    }
}
