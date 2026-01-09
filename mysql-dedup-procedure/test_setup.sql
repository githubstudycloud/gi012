-- ============================================================================
-- 测试环境设置：创建测试数据库和表
-- MySQL 5.7 兼容
-- ============================================================================

-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS test_dedup DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE test_dedup;

-- ============================================================================
-- 创建测试表1：订单表（order_id + item_id 作为复合主键）
-- ============================================================================
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id VARCHAR(32) NOT NULL COMMENT '订单ID',
    item_id INT NOT NULL COMMENT '商品ID',
    amount DECIMAL(10,2) NOT NULL COMMENT '金额',
    created_at DATETIME NOT NULL COMMENT '创建时间',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态',
    PRIMARY KEY (order_id, item_id),
    INDEX idx_order_id (order_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- ============================================================================
-- 插入测试数据（包含重复订单号的记录）
-- ============================================================================
INSERT INTO orders (order_id, item_id, amount, created_at, status) VALUES
-- 订单 ORD001 有3条记录（商品ID不同），保留最新的
('ORD001', 101, 100.00, '2024-01-01 10:00:00', 'completed'),
('ORD001', 102, 150.00, '2024-01-05 14:00:00', 'completed'),
('ORD001', 103, 200.00, '2024-01-10 09:00:00', 'pending'),

-- 订单 ORD002 有2条记录
('ORD002', 201, 300.00, '2024-01-02 11:00:00', 'completed'),
('ORD002', 202, 250.00, '2024-01-08 16:00:00', 'pending'),

-- 订单 ORD003 只有1条记录（不应被删除）
('ORD003', 301, 400.00, '2024-01-03 12:00:00', 'completed'),

-- 订单 ORD004 有4条记录
('ORD004', 401, 50.00, '2024-01-01 08:00:00', 'cancelled'),
('ORD004', 402, 75.00, '2024-01-03 10:00:00', 'completed'),
('ORD004', 403, 80.00, '2024-01-07 15:00:00', 'completed'),
('ORD004', 404, 90.00, '2024-01-15 18:00:00', 'pending'),

-- 订单 ORD005 只有1条记录（不应被删除）
('ORD005', 501, 500.00, '2024-01-04 13:00:00', 'completed');

-- ============================================================================
-- 创建测试表2：用户活动表（user_id + activity_id 作为复合主键）
-- ============================================================================
DROP TABLE IF EXISTS user_activities;

CREATE TABLE user_activities (
    user_id INT NOT NULL COMMENT '用户ID',
    activity_id INT NOT NULL COMMENT '活动ID',
    points INT NOT NULL COMMENT '积分',
    activity_time DATETIME NOT NULL COMMENT '活动时间',
    remark VARCHAR(255) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (user_id, activity_id),
    INDEX idx_user_id (user_id),
    INDEX idx_activity_time (activity_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户活动表';

-- 插入测试数据
INSERT INTO user_activities (user_id, activity_id, points, activity_time, remark) VALUES
-- 用户1 有多条活动记录
(1, 1001, 10, '2024-01-01 09:00:00', '签到'),
(1, 1002, 20, '2024-01-05 10:00:00', '分享'),
(1, 1003, 50, '2024-01-10 11:00:00', '购买'),

-- 用户2 有2条记录
(2, 2001, 15, '2024-01-02 08:00:00', '签到'),
(2, 2002, 30, '2024-01-08 12:00:00', '评论'),

-- 用户3 只有1条记录
(3, 3001, 25, '2024-01-03 14:00:00', '注册');

-- ============================================================================
-- 验证测试数据
-- ============================================================================
SELECT '=== 订单表数据 ===' AS info;
SELECT * FROM orders ORDER BY order_id, created_at;

SELECT '=== 订单表重复统计 ===' AS info;
SELECT order_id, COUNT(*) AS cnt
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

SELECT '=== 用户活动表数据 ===' AS info;
SELECT * FROM user_activities ORDER BY user_id, activity_time;

SELECT '=== 用户活动表重复统计 ===' AS info;
SELECT user_id, COUNT(*) AS cnt
FROM user_activities
GROUP BY user_id
HAVING COUNT(*) > 1;
