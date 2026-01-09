-- ============================================================================
-- 测试执行脚本：测试存储过程功能
-- MySQL 5.7 兼容
-- ============================================================================

USE test_dedup;

-- 加载存储过程（需要先执行）
-- SOURCE sp_cleanup_duplicate_records.sql;

-- ============================================================================
-- 测试1：使用临时表 + 测试模式（不实际删除）
-- ============================================================================
SELECT '========================================' AS divider;
SELECT '测试1: 临时表 + 测试模式 (dry run)' AS test_name;
SELECT '========================================' AS divider;

-- 查看删除前的数据
SELECT '删除前 - 订单表数据:' AS info;
SELECT * FROM orders ORDER BY order_id, created_at;

CALL sp_cleanup_duplicate_records(
    'orders',           -- 表名
    'order_id',         -- 主键字段1
    'item_id',          -- 主键字段2
    'created_at',       -- 日期字段
    1,                  -- 使用临时表
    NULL,               -- 中间表名（临时表模式忽略）
    1,                  -- 测试模式
    @groups1, @to_delete1, @deleted1
);

SELECT @groups1 AS duplicate_groups, @to_delete1 AS to_delete, @deleted1 AS deleted;

-- 验证数据未被删除
SELECT '测试模式后 - 订单表数据（应保持不变）:' AS info;
SELECT COUNT(*) AS total_records FROM orders;

-- ============================================================================
-- 测试2：使用实际表 + 测试模式
-- ============================================================================
SELECT '========================================' AS divider;
SELECT '测试2: 实际表 + 测试模式' AS test_name;
SELECT '========================================' AS divider;

CALL sp_cleanup_duplicate_records(
    'orders',
    'order_id',
    'item_id',
    'created_at',
    0,                  -- 使用实际表
    'orders_staging',   -- 中间表名
    1,                  -- 测试模式
    @groups2, @to_delete2, @deleted2
);

SELECT @groups2 AS duplicate_groups, @to_delete2 AS to_delete, @deleted2 AS deleted;

-- 查看中间表（实际表模式会保留）
SELECT '中间表内容:' AS info;
SELECT * FROM orders_staging;

-- ============================================================================
-- 测试3：使用辅助存储过程
-- ============================================================================
SELECT '========================================' AS divider;
SELECT '测试3: 辅助存储过程 sp_get_duplicate_records' AS test_name;
SELECT '========================================' AS divider;

CALL sp_get_duplicate_records(
    'orders',
    'order_id',
    'item_id',
    'created_at',
    'orders_dup_temp',
    @cnt
);

SELECT @cnt AS records_found;
SELECT * FROM orders_dup_temp;

-- ============================================================================
-- 测试4：实际执行删除
-- ============================================================================
SELECT '========================================' AS divider;
SELECT '测试4: 实际执行删除' AS test_name;
SELECT '========================================' AS divider;

SELECT '删除前订单数:' AS info;
SELECT COUNT(*) AS before_count FROM orders;

CALL sp_cleanup_duplicate_records(
    'orders',
    'order_id',
    'item_id',
    'created_at',
    0,                  -- 使用实际表
    'orders_deleted',   -- 保存已删除记录
    0,                  -- 实际执行
    @groups4, @to_delete4, @deleted4
);

SELECT @groups4 AS duplicate_groups, @to_delete4 AS to_delete, @deleted4 AS deleted;

SELECT '删除后订单数:' AS info;
SELECT COUNT(*) AS after_count FROM orders;

SELECT '删除后剩余数据（每个订单只保留最新记录）:' AS info;
SELECT * FROM orders ORDER BY order_id;

SELECT '已删除的记录（保存在 orders_deleted 表中）:' AS info;
SELECT * FROM orders_deleted;

-- ============================================================================
-- 测试5：测试 sp_delete_by_staging
-- ============================================================================
SELECT '========================================' AS divider;
SELECT '测试5: sp_delete_by_staging 辅助过程' AS test_name;
SELECT '========================================' AS divider;

-- 重新设置用户活动表的测试数据
SELECT '用户活动表删除前:' AS info;
SELECT * FROM user_activities ORDER BY user_id, activity_time;

-- 先获取待删除记录
CALL sp_get_duplicate_records(
    'user_activities',
    'user_id',
    'activity_id',
    'activity_time',
    'user_activities_staging',
    @cnt5
);

SELECT @cnt5 AS records_to_delete;
SELECT '待删除记录:' AS info;
SELECT * FROM user_activities_staging;

-- 执行删除
CALL sp_delete_by_staging(
    'user_activities',
    'user_id',
    'activity_id',
    'user_activities_staging',
    @deleted5
);

SELECT @deleted5 AS records_deleted;

SELECT '用户活动表删除后（每个用户只保留最新记录）:' AS info;
SELECT * FROM user_activities ORDER BY user_id;

-- ============================================================================
-- 测试6：无重复数据的情况
-- ============================================================================
SELECT '========================================' AS divider;
SELECT '测试6: 无重复数据' AS test_name;
SELECT '========================================' AS divider;

-- 此时 orders 表已无重复
CALL sp_cleanup_duplicate_records(
    'orders',
    'order_id',
    'item_id',
    'created_at',
    1,
    NULL,
    1,
    @groups6, @to_delete6, @deleted6
);

SELECT @groups6 AS duplicate_groups, @to_delete6 AS to_delete, @deleted6 AS deleted;

SELECT '========================================' AS divider;
SELECT '所有测试完成!' AS result;
SELECT '========================================' AS divider;
