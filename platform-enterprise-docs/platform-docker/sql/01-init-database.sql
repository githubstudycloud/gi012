-- Platform Enterprise 数据库初始化脚本
-- PostgreSQL 17

-- 创建数据库（如果不存在）
-- CREATE DATABASE platform;

-- 连接到 platform 数据库
\c platform;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==================== 用户模块 ====================

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(64) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    nickname        VARCHAR(64),
    email           VARCHAR(128) UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    avatar          VARCHAR(512),
    gender          SMALLINT DEFAULT 0,          -- 0:未知, 1:男, 2:女
    status          SMALLINT DEFAULT 1,          -- 0:禁用, 1:启用
    dept_id         BIGINT,
    last_login_time TIMESTAMP,
    last_login_ip   VARCHAR(64),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted         SMALLINT DEFAULT 0           -- 0:正常, 1:已删除
);

CREATE INDEX idx_sys_user_username ON sys_user(username);
CREATE INDEX idx_sys_user_phone ON sys_user(phone);
CREATE INDEX idx_sys_user_email ON sys_user(email);
CREATE INDEX idx_sys_user_dept_id ON sys_user(dept_id);
CREATE INDEX idx_sys_user_status ON sys_user(status);

COMMENT ON TABLE sys_user IS '系统用户表';
COMMENT ON COLUMN sys_user.username IS '用户名';
COMMENT ON COLUMN sys_user.password IS '密码（BCrypt加密）';
COMMENT ON COLUMN sys_user.nickname IS '昵称';
COMMENT ON COLUMN sys_user.email IS '邮箱';
COMMENT ON COLUMN sys_user.phone IS '手机号';
COMMENT ON COLUMN sys_user.avatar IS '头像URL';
COMMENT ON COLUMN sys_user.gender IS '性别：0未知,1男,2女';
COMMENT ON COLUMN sys_user.status IS '状态：0禁用,1启用';

-- 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(64) NOT NULL,
    code        VARCHAR(64) NOT NULL UNIQUE,
    description VARCHAR(255),
    sort        INT DEFAULT 0,
    status      SMALLINT DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by  BIGINT,
    updated_by  BIGINT,
    deleted     SMALLINT DEFAULT 0
);

CREATE INDEX idx_sys_role_code ON sys_role(code);
CREATE INDEX idx_sys_role_status ON sys_role(status);

COMMENT ON TABLE sys_role IS '系统角色表';
COMMENT ON COLUMN sys_role.name IS '角色名称';
COMMENT ON COLUMN sys_role.code IS '角色编码';
COMMENT ON COLUMN sys_role.description IS '角色描述';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS sys_user_role (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    role_id    BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_sys_user_role_user_id ON sys_user_role(user_id);
CREATE INDEX idx_sys_user_role_role_id ON sys_user_role(role_id);

COMMENT ON TABLE sys_user_role IS '用户角色关联表';

-- 菜单权限表
CREATE TABLE IF NOT EXISTS sys_menu (
    id          BIGSERIAL PRIMARY KEY,
    parent_id   BIGINT DEFAULT 0,
    name        VARCHAR(64) NOT NULL,
    path        VARCHAR(255),
    component   VARCHAR(255),
    redirect    VARCHAR(255),
    icon        VARCHAR(64),
    type        SMALLINT NOT NULL,              -- 1:目录, 2:菜单, 3:按钮
    permission  VARCHAR(128),
    sort        INT DEFAULT 0,
    visible     SMALLINT DEFAULT 1,             -- 0:隐藏, 1:显示
    status      SMALLINT DEFAULT 1,
    keep_alive  SMALLINT DEFAULT 0,
    external    SMALLINT DEFAULT 0,             -- 是否外链
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by  BIGINT,
    updated_by  BIGINT,
    deleted     SMALLINT DEFAULT 0
);

CREATE INDEX idx_sys_menu_parent_id ON sys_menu(parent_id);
CREATE INDEX idx_sys_menu_type ON sys_menu(type);
CREATE INDEX idx_sys_menu_status ON sys_menu(status);

COMMENT ON TABLE sys_menu IS '系统菜单权限表';
COMMENT ON COLUMN sys_menu.type IS '类型：1目录,2菜单,3按钮';
COMMENT ON COLUMN sys_menu.permission IS '权限标识';

-- 角色菜单关联表
CREATE TABLE IF NOT EXISTS sys_role_menu (
    id         BIGSERIAL PRIMARY KEY,
    role_id    BIGINT NOT NULL,
    menu_id    BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, menu_id)
);

CREATE INDEX idx_sys_role_menu_role_id ON sys_role_menu(role_id);
CREATE INDEX idx_sys_role_menu_menu_id ON sys_role_menu(menu_id);

COMMENT ON TABLE sys_role_menu IS '角色菜单关联表';

-- 部门表
CREATE TABLE IF NOT EXISTS sys_dept (
    id          BIGSERIAL PRIMARY KEY,
    parent_id   BIGINT DEFAULT 0,
    ancestors   VARCHAR(512),                   -- 祖级列表
    name        VARCHAR(64) NOT NULL,
    sort        INT DEFAULT 0,
    leader      VARCHAR(64),
    phone       VARCHAR(20),
    email       VARCHAR(128),
    status      SMALLINT DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by  BIGINT,
    updated_by  BIGINT,
    deleted     SMALLINT DEFAULT 0
);

CREATE INDEX idx_sys_dept_parent_id ON sys_dept(parent_id);
CREATE INDEX idx_sys_dept_status ON sys_dept(status);

COMMENT ON TABLE sys_dept IS '部门表';
COMMENT ON COLUMN sys_dept.ancestors IS '祖级ID路径，如:0,1,2';

-- ==================== 系统日志模块 ====================

-- 操作日志表
CREATE TABLE IF NOT EXISTS sys_operation_log (
    id              BIGSERIAL PRIMARY KEY,
    module          VARCHAR(64),                -- 模块
    title           VARCHAR(255),               -- 操作标题
    business_type   SMALLINT DEFAULT 0,         -- 业务类型
    method          VARCHAR(255),               -- 方法名
    request_method  VARCHAR(10),                -- 请求方式
    operator_type   SMALLINT DEFAULT 0,         -- 操作类别
    operator_name   VARCHAR(64),                -- 操作人
    operator_id     BIGINT,
    dept_name       VARCHAR(64),
    url             VARCHAR(512),
    ip              VARCHAR(64),
    location        VARCHAR(255),
    request_param   TEXT,
    response_result TEXT,
    status          SMALLINT DEFAULT 1,         -- 0:异常, 1:正常
    error_msg       TEXT,
    cost_time       BIGINT,                     -- 耗时(ms)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_operation_log_operator_id ON sys_operation_log(operator_id);
CREATE INDEX idx_sys_operation_log_created_at ON sys_operation_log(created_at);
CREATE INDEX idx_sys_operation_log_status ON sys_operation_log(status);

COMMENT ON TABLE sys_operation_log IS '操作日志表';

-- 登录日志表
CREATE TABLE IF NOT EXISTS sys_login_log (
    id          BIGSERIAL PRIMARY KEY,
    username    VARCHAR(64),
    ip          VARCHAR(64),
    location    VARCHAR(255),
    browser     VARCHAR(64),
    os          VARCHAR(64),
    status      SMALLINT DEFAULT 1,             -- 0:失败, 1:成功
    msg         VARCHAR(512),
    login_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_login_log_username ON sys_login_log(username);
CREATE INDEX idx_sys_login_log_login_time ON sys_login_log(login_time);
CREATE INDEX idx_sys_login_log_status ON sys_login_log(status);

COMMENT ON TABLE sys_login_log IS '登录日志表';

-- ==================== 字典模块 ====================

-- 字典类型表
CREATE TABLE IF NOT EXISTS sys_dict_type (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    type        VARCHAR(128) NOT NULL UNIQUE,
    remark      VARCHAR(512),
    status      SMALLINT DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by  BIGINT,
    updated_by  BIGINT,
    deleted     SMALLINT DEFAULT 0
);

CREATE INDEX idx_sys_dict_type_type ON sys_dict_type(type);

COMMENT ON TABLE sys_dict_type IS '字典类型表';

-- 字典数据表
CREATE TABLE IF NOT EXISTS sys_dict_data (
    id           BIGSERIAL PRIMARY KEY,
    dict_type    VARCHAR(128) NOT NULL,
    label        VARCHAR(128) NOT NULL,
    value        VARCHAR(128) NOT NULL,
    css_class    VARCHAR(128),
    list_class   VARCHAR(128),
    sort         INT DEFAULT 0,
    is_default   SMALLINT DEFAULT 0,
    status       SMALLINT DEFAULT 1,
    remark       VARCHAR(512),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by   BIGINT,
    updated_by   BIGINT,
    deleted      SMALLINT DEFAULT 0
);

CREATE INDEX idx_sys_dict_data_dict_type ON sys_dict_data(dict_type);

COMMENT ON TABLE sys_dict_data IS '字典数据表';

-- ==================== 文件模块 ====================

-- 文件记录表
CREATE TABLE IF NOT EXISTS sys_file (
    id           BIGSERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    extension    VARCHAR(32),
    size         BIGINT,
    content_type VARCHAR(128),
    bucket       VARCHAR(64),
    path         VARCHAR(512) NOT NULL,
    url          VARCHAR(1024),
    md5          VARCHAR(64),
    upload_by    BIGINT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_file_md5 ON sys_file(md5);
CREATE INDEX idx_sys_file_upload_by ON sys_file(upload_by);
CREATE INDEX idx_sys_file_created_at ON sys_file(created_at);

COMMENT ON TABLE sys_file IS '文件记录表';

-- ==================== 创建更新时间触发器 ====================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有需要的表创建触发器
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END;
$$;

COMMIT;
