package com.platform.user.converter;

import com.platform.user.dto.UserCreateRequest;
import com.platform.user.dto.UserDTO;
import com.platform.user.entity.User;
import org.mapstruct.*;

import java.util.List;

/**
 * 用户对象转换器
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Mapper(componentModel = "spring",
        nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
public interface UserConverter {

    /**
     * Entity 转 DTO
     */
    UserDTO toDTO(User user);

    /**
     * Entity 列表转 DTO 列表
     */
    List<UserDTO> toDTOList(List<User> users);

    /**
     * CreateRequest 转 Entity
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "password", ignore = true)
    @Mapping(target = "status", ignore = true)
    @Mapping(target = "lastLoginAt", ignore = true)
    @Mapping(target = "lastLoginIp", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "createdBy", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    @Mapping(target = "updatedBy", ignore = true)
    @Mapping(target = "deleted", ignore = true)
    @Mapping(target = "tenantId", ignore = true)
    User toEntity(UserCreateRequest request);

    /**
     * 更新 Entity
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "password", ignore = true)
    @Mapping(target = "status", ignore = true)
    @Mapping(target = "lastLoginAt", ignore = true)
    @Mapping(target = "lastLoginIp", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "createdBy", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    @Mapping(target = "updatedBy", ignore = true)
    @Mapping(target = "deleted", ignore = true)
    @Mapping(target = "tenantId", ignore = true)
    void updateEntity(UserCreateRequest request, @MappingTarget User user);
}
