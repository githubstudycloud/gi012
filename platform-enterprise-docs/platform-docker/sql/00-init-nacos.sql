-- Nacos 数据库初始化脚本
-- PostgreSQL 17

-- 创建 Nacos 数据库
CREATE DATABASE nacos;

\c nacos;

-- Nacos 配置表
CREATE TABLE config_info (
    id                 BIGSERIAL PRIMARY KEY,
    data_id            VARCHAR(255) NOT NULL,
    group_id           VARCHAR(128) DEFAULT NULL,
    content            TEXT NOT NULL,
    md5                VARCHAR(32) DEFAULT NULL,
    gmt_create         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gmt_modified       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    src_user           TEXT,
    src_ip             VARCHAR(50) DEFAULT NULL,
    app_name           VARCHAR(128) DEFAULT NULL,
    tenant_id          VARCHAR(128) DEFAULT '',
    c_desc             VARCHAR(256) DEFAULT NULL,
    c_use              VARCHAR(64) DEFAULT NULL,
    effect             VARCHAR(64) DEFAULT NULL,
    type               VARCHAR(64) DEFAULT NULL,
    c_schema           TEXT,
    encrypted_data_key TEXT DEFAULT NULL,
    UNIQUE(data_id, group_id, tenant_id)
);

CREATE INDEX idx_config_info_data_id ON config_info(data_id);
CREATE INDEX idx_config_info_group_id ON config_info(group_id);
CREATE INDEX idx_config_info_tenant_id ON config_info(tenant_id);
CREATE INDEX idx_config_info_app_name ON config_info(app_name);

-- 配置标签表
CREATE TABLE config_tags_relation (
    id        BIGSERIAL PRIMARY KEY,
    tag_name  VARCHAR(128) NOT NULL,
    tag_type  VARCHAR(64) DEFAULT NULL,
    data_id   VARCHAR(255) NOT NULL,
    group_id  VARCHAR(128) NOT NULL,
    tenant_id VARCHAR(128) DEFAULT '',
    nid       BIGINT NOT NULL
);

CREATE UNIQUE INDEX uk_config_tags ON config_tags_relation(tag_name, tag_type, data_id, group_id, tenant_id);
CREATE INDEX idx_tenant_id ON config_tags_relation(tenant_id);

-- 配置历史表
CREATE TABLE his_config_info (
    id                 BIGINT NOT NULL,
    nid                BIGSERIAL PRIMARY KEY,
    data_id            VARCHAR(255) NOT NULL,
    group_id           VARCHAR(128) NOT NULL,
    app_name           VARCHAR(128) DEFAULT NULL,
    content            TEXT NOT NULL,
    md5                VARCHAR(32) DEFAULT NULL,
    gmt_create         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gmt_modified       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    src_user           TEXT,
    src_ip             VARCHAR(50) DEFAULT NULL,
    op_type            CHAR(10) DEFAULT NULL,
    tenant_id          VARCHAR(128) DEFAULT '',
    encrypted_data_key TEXT DEFAULT NULL
);

CREATE INDEX idx_his_config_info_data_id ON his_config_info(data_id);
CREATE INDEX idx_his_config_info_gmt_create ON his_config_info(gmt_create);
CREATE INDEX idx_his_config_info_gmt_modified ON his_config_info(gmt_modified);

-- 聚合配置表
CREATE TABLE config_info_aggr (
    id           BIGSERIAL PRIMARY KEY,
    data_id      VARCHAR(255) NOT NULL,
    group_id     VARCHAR(128) NOT NULL,
    datum_id     VARCHAR(255) NOT NULL,
    content      TEXT NOT NULL,
    gmt_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    app_name     VARCHAR(128) DEFAULT NULL,
    tenant_id    VARCHAR(128) DEFAULT '',
    UNIQUE(data_id, group_id, tenant_id, datum_id)
);

-- Beta 配置表
CREATE TABLE config_info_beta (
    id                 BIGSERIAL PRIMARY KEY,
    data_id            VARCHAR(255) NOT NULL,
    group_id           VARCHAR(128) NOT NULL,
    app_name           VARCHAR(128) DEFAULT NULL,
    content            TEXT NOT NULL,
    beta_ips           VARCHAR(1024) DEFAULT NULL,
    md5                VARCHAR(32) DEFAULT NULL,
    gmt_create         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gmt_modified       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    src_user           TEXT,
    src_ip             VARCHAR(50) DEFAULT NULL,
    tenant_id          VARCHAR(128) DEFAULT '',
    encrypted_data_key TEXT DEFAULT NULL,
    UNIQUE(data_id, group_id, tenant_id)
);

-- 标签配置表
CREATE TABLE config_info_tag (
    id                 BIGSERIAL PRIMARY KEY,
    data_id            VARCHAR(255) NOT NULL,
    group_id           VARCHAR(128) NOT NULL,
    tenant_id          VARCHAR(128) DEFAULT '',
    tag_id             VARCHAR(128) NOT NULL,
    app_name           VARCHAR(128) DEFAULT NULL,
    content            TEXT NOT NULL,
    md5                VARCHAR(32) DEFAULT NULL,
    gmt_create         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gmt_modified       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    src_user           TEXT,
    src_ip             VARCHAR(50) DEFAULT NULL,
    UNIQUE(data_id, group_id, tenant_id, tag_id)
);

-- 租户容量表
CREATE TABLE tenant_capacity (
    id                BIGSERIAL PRIMARY KEY,
    tenant_id         VARCHAR(128) NOT NULL DEFAULT '' UNIQUE,
    quota             INT NOT NULL DEFAULT 0,
    usage             INT NOT NULL DEFAULT 0,
    max_size          INT NOT NULL DEFAULT 0,
    max_aggr_count    INT NOT NULL DEFAULT 0,
    max_aggr_size     INT NOT NULL DEFAULT 0,
    max_history_count INT NOT NULL DEFAULT 0,
    gmt_create        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gmt_modified      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 组容量表
CREATE TABLE group_capacity (
    id                BIGSERIAL PRIMARY KEY,
    group_id          VARCHAR(128) NOT NULL DEFAULT '' UNIQUE,
    quota             INT NOT NULL DEFAULT 0,
    usage             INT NOT NULL DEFAULT 0,
    max_size          INT NOT NULL DEFAULT 0,
    max_aggr_count    INT NOT NULL DEFAULT 0,
    max_aggr_size     INT NOT NULL DEFAULT 0,
    max_history_count INT NOT NULL DEFAULT 0,
    gmt_create        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gmt_modified      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 租户信息表
CREATE TABLE tenant_info (
    id            BIGSERIAL PRIMARY KEY,
    kp            VARCHAR(128) NOT NULL,
    tenant_id     VARCHAR(128) DEFAULT '',
    tenant_name   VARCHAR(128) DEFAULT '',
    tenant_desc   VARCHAR(256) DEFAULT NULL,
    create_source VARCHAR(32) DEFAULT NULL,
    gmt_create    BIGINT NOT NULL,
    gmt_modified  BIGINT NOT NULL,
    UNIQUE(kp, tenant_id)
);

CREATE INDEX idx_tenant_info_tenant_id ON tenant_info(tenant_id);

-- 用户表
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(500) NOT NULL,
    enabled  BOOLEAN NOT NULL
);

-- 角色表
CREATE TABLE roles (
    username VARCHAR(50) NOT NULL,
    role     VARCHAR(50) NOT NULL,
    UNIQUE(username, role)
);

-- 权限表
CREATE TABLE permissions (
    role     VARCHAR(50) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    action   VARCHAR(8) NOT NULL,
    UNIQUE(role, resource, action)
);

-- 初始化 Nacos 用户（密码: nacos）
INSERT INTO users (username, password, enabled) VALUES
('nacos', '$2a$10$EuWPZHzz32dJN7jexM34MOeYirDdFAZm2kuWj7VEOJhhZkDrxfvUu', true);

INSERT INTO roles (username, role) VALUES
('nacos', 'ROLE_ADMIN');

COMMIT;
