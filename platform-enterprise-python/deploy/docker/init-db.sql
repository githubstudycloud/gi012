-- 创建各服务数据库
CREATE DATABASE platform_auth;
CREATE DATABASE platform_user;
CREATE DATABASE platform_notification;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE platform_auth TO postgres;
GRANT ALL PRIVILEGES ON DATABASE platform_user TO postgres;
GRANT ALL PRIVILEGES ON DATABASE platform_notification TO postgres;
