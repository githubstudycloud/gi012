-- Platform Enterprise 初始数据
-- PostgreSQL 17

\c platform;

-- ==================== 初始化部门 ====================
INSERT INTO sys_dept (id, parent_id, ancestors, name, sort, leader, status) VALUES
(1, 0, '0', '总公司', 1, '管理员', 1),
(2, 1, '0,1', '技术部', 1, NULL, 1),
(3, 1, '0,1', '产品部', 2, NULL, 1),
(4, 1, '0,1', '运营部', 3, NULL, 1),
(5, 2, '0,1,2', '研发组', 1, NULL, 1),
(6, 2, '0,1,2', '测试组', 2, NULL, 1);

-- 重置序列
SELECT setval('sys_dept_id_seq', 100);

-- ==================== 初始化角色 ====================
INSERT INTO sys_role (id, name, code, description, sort, status) VALUES
(1, '超级管理员', 'SUPER_ADMIN', '拥有所有权限', 1, 1),
(2, '系统管理员', 'ADMIN', '系统管理权限', 2, 1),
(3, '普通用户', 'USER', '普通用户权限', 3, 1);

SELECT setval('sys_role_id_seq', 100);

-- ==================== 初始化用户 ====================
-- 密码: admin123 (BCrypt加密)
INSERT INTO sys_user (id, username, password, nickname, email, phone, avatar, gender, status, dept_id) VALUES
(1, 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '超级管理员', 'admin@platform.com', '13800000001', NULL, 1, 1, 1),
(2, 'zhangsan', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '张三', 'zhangsan@platform.com', '13800000002', NULL, 1, 1, 5),
(3, 'lisi', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '李四', 'lisi@platform.com', '13800000003', NULL, 1, 1, 5);

SELECT setval('sys_user_id_seq', 100);

-- ==================== 初始化用户角色关联 ====================
INSERT INTO sys_user_role (user_id, role_id) VALUES
(1, 1),  -- admin -> 超级管理员
(2, 2),  -- zhangsan -> 系统管理员
(3, 3);  -- lisi -> 普通用户

-- ==================== 初始化菜单 ====================
-- 一级菜单
INSERT INTO sys_menu (id, parent_id, name, path, component, icon, type, permission, sort, visible, status) VALUES
-- 系统管理
(1, 0, '系统管理', '/system', 'Layout', 'Setting', 1, NULL, 1, 1, 1),
(2, 0, '系统监控', '/monitor', 'Layout', 'Monitor', 1, NULL, 2, 1, 1),
(3, 0, '系统工具', '/tool', 'Layout', 'Tools', 1, NULL, 3, 1, 1);

-- 系统管理子菜单
INSERT INTO sys_menu (id, parent_id, name, path, component, icon, type, permission, sort, visible, status) VALUES
(101, 1, '用户管理', 'user', 'system/user/index', 'User', 2, 'system:user:list', 1, 1, 1),
(102, 1, '角色管理', 'role', 'system/role/index', 'UserFilled', 2, 'system:role:list', 2, 1, 1),
(103, 1, '菜单管理', 'menu', 'system/menu/index', 'Menu', 2, 'system:menu:list', 3, 1, 1),
(104, 1, '部门管理', 'dept', 'system/dept/index', 'OfficeBuilding', 2, 'system:dept:list', 4, 1, 1),
(105, 1, '字典管理', 'dict', 'system/dict/index', 'Collection', 2, 'system:dict:list', 5, 1, 1);

-- 系统监控子菜单
INSERT INTO sys_menu (id, parent_id, name, path, component, icon, type, permission, sort, visible, status) VALUES
(201, 2, '在线用户', 'online', 'monitor/online/index', 'Connection', 2, 'monitor:online:list', 1, 1, 1),
(202, 2, '服务监控', 'server', 'monitor/server/index', 'Cpu', 2, 'monitor:server:list', 2, 1, 1),
(203, 2, '操作日志', 'operlog', 'monitor/operlog/index', 'Document', 2, 'monitor:operlog:list', 3, 1, 1),
(204, 2, '登录日志', 'loginlog', 'monitor/loginlog/index', 'Key', 2, 'monitor:loginlog:list', 4, 1, 1);

-- 系统工具子菜单
INSERT INTO sys_menu (id, parent_id, name, path, component, icon, type, permission, sort, visible, status) VALUES
(301, 3, '表单构建', 'form', 'tool/form/index', 'Edit', 2, 'tool:form:list', 1, 1, 1),
(302, 3, '代码生成', 'gen', 'tool/gen/index', 'Promotion', 2, 'tool:gen:list', 2, 1, 1),
(303, 3, 'API文档', 'swagger', 'tool/swagger/index', 'Link', 2, 'tool:swagger:list', 3, 1, 1);

-- 用户管理按钮
INSERT INTO sys_menu (id, parent_id, name, path, component, icon, type, permission, sort, visible, status) VALUES
(1011, 101, '用户查询', '', NULL, '', 3, 'system:user:query', 1, 1, 1),
(1012, 101, '用户新增', '', NULL, '', 3, 'system:user:add', 2, 1, 1),
(1013, 101, '用户修改', '', NULL, '', 3, 'system:user:edit', 3, 1, 1),
(1014, 101, '用户删除', '', NULL, '', 3, 'system:user:delete', 4, 1, 1),
(1015, 101, '用户导出', '', NULL, '', 3, 'system:user:export', 5, 1, 1),
(1016, 101, '重置密码', '', NULL, '', 3, 'system:user:resetPwd', 6, 1, 1);

-- 角色管理按钮
INSERT INTO sys_menu (id, parent_id, name, path, component, icon, type, permission, sort, visible, status) VALUES
(1021, 102, '角色查询', '', NULL, '', 3, 'system:role:query', 1, 1, 1),
(1022, 102, '角色新增', '', NULL, '', 3, 'system:role:add', 2, 1, 1),
(1023, 102, '角色修改', '', NULL, '', 3, 'system:role:edit', 3, 1, 1),
(1024, 102, '角色删除', '', NULL, '', 3, 'system:role:delete', 4, 1, 1),
(1025, 102, '角色导出', '', NULL, '', 3, 'system:role:export', 5, 1, 1);

-- 菜单管理按钮
INSERT INTO sys_menu (id, parent_id, name, path, component, icon, type, permission, sort, visible, status) VALUES
(1031, 103, '菜单查询', '', NULL, '', 3, 'system:menu:query', 1, 1, 1),
(1032, 103, '菜单新增', '', NULL, '', 3, 'system:menu:add', 2, 1, 1),
(1033, 103, '菜单修改', '', NULL, '', 3, 'system:menu:edit', 3, 1, 1),
(1034, 103, '菜单删除', '', NULL, '', 3, 'system:menu:delete', 4, 1, 1);

SELECT setval('sys_menu_id_seq', 10000);

-- ==================== 初始化角色菜单关联 ====================
-- 超级管理员拥有所有菜单权限
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, id FROM sys_menu;

-- 系统管理员拥有系统管理权限
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 2, id FROM sys_menu WHERE id IN (1, 101, 102, 103, 104, 105, 1011, 1012, 1013, 1014, 1021, 1022, 1023, 1024, 1031, 1032, 1033, 1034);

-- 普通用户只有查看权限
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 3, id FROM sys_menu WHERE id IN (1, 101, 1011);

-- ==================== 初始化字典类型 ====================
INSERT INTO sys_dict_type (id, name, type, remark, status) VALUES
(1, '用户性别', 'sys_user_gender', '用户性别列表', 1),
(2, '系统开关', 'sys_normal_disable', '系统开关列表', 1),
(3, '系统是否', 'sys_yes_no', '系统是否列表', 1),
(4, '菜单类型', 'sys_menu_type', '菜单类型列表', 1),
(5, '操作类型', 'sys_oper_type', '操作类型列表', 1),
(6, '登录状态', 'sys_login_status', '登录状态列表', 1);

SELECT setval('sys_dict_type_id_seq', 100);

-- ==================== 初始化字典数据 ====================
INSERT INTO sys_dict_data (dict_type, label, value, sort, is_default, status) VALUES
-- 用户性别
('sys_user_gender', '未知', '0', 1, 1, 1),
('sys_user_gender', '男', '1', 2, 0, 1),
('sys_user_gender', '女', '2', 3, 0, 1),
-- 系统开关
('sys_normal_disable', '正常', '1', 1, 1, 1),
('sys_normal_disable', '停用', '0', 2, 0, 1),
-- 系统是否
('sys_yes_no', '是', '1', 1, 1, 1),
('sys_yes_no', '否', '0', 2, 0, 1),
-- 菜单类型
('sys_menu_type', '目录', '1', 1, 0, 1),
('sys_menu_type', '菜单', '2', 2, 0, 1),
('sys_menu_type', '按钮', '3', 3, 0, 1),
-- 操作类型
('sys_oper_type', '其他', '0', 1, 0, 1),
('sys_oper_type', '新增', '1', 2, 0, 1),
('sys_oper_type', '修改', '2', 3, 0, 1),
('sys_oper_type', '删除', '3', 4, 0, 1),
('sys_oper_type', '授权', '4', 5, 0, 1),
('sys_oper_type', '导出', '5', 6, 0, 1),
('sys_oper_type', '导入', '6', 7, 0, 1),
-- 登录状态
('sys_login_status', '成功', '1', 1, 0, 1),
('sys_login_status', '失败', '0', 2, 0, 1);

COMMIT;
