# MySQL 5.7 重复数据清理存储过程

清理具有复合主键和日期字段的表中的重复数据，保留最新记录。

## 功能特性

- 支持任意表名、字段名的动态处理
- 支持临时表和实际表两种中间表模式
- 支持测试模式（dry run）和实际执行模式
- 三层架构：核心版(core)、标准版、静默版(silent)
- 静默版无任何输出，适合 Java/程序调用
- MySQL 5.7 完全兼容

## 文件说明

| 文件 | 说明 |
|------|------|
| `sp_cleanup_duplicate_records.sql` | 存储过程定义（12个） |
| `test_setup.sql` | 测试数据库和测试数据 |
| `test_run.sql` | 测试执行脚本 |

## 存储过程列表

### 主流程：清理重复记录

| 存储过程 | 说明 | OUT参数 | 输出结果集 |
|---------|------|---------|-----------|
| `sp_cleanup_duplicate_records_core` | 核心逻辑 | 有 | 无 |
| `sp_cleanup_duplicate_records` | 标准版（调试用） | 有 | 有 |
| `sp_cleanup_duplicate_records_silent` | **静默版（Java推荐）** | 无 | **无** |

### 辅助：获取重复记录到中间表

| 存储过程 | 说明 | OUT参数 | 输出结果集 |
|---------|------|---------|-----------|
| `sp_get_duplicate_records_core` | 核心逻辑 | 有 | 无 |
| `sp_get_duplicate_records` | 标准版 | 有 | 有 |
| `sp_get_duplicate_records_silent` | **静默版（Java推荐）** | 无 | **无** |

### 辅助：根据中间表删除

| 存储过程 | 说明 | OUT参数 | 输出结果集 |
|---------|------|---------|-----------|
| `sp_delete_by_staging_core` | 核心逻辑 | 有 | 无 |
| `sp_delete_by_staging` | 标准版 | 有 | 有 |
| `sp_delete_by_staging_silent` | **静默版（Java推荐）** | 无 | **无** |

## 参数说明

### `sp_cleanup_duplicate_records_silent`

```sql
CALL sp_cleanup_duplicate_records_silent(
    'table_name',      -- 目标表名
    'pk_field1',       -- 主键字段1（用于分组）
    'pk_field2',       -- 主键字段2
    'date_field',      -- 日期字段
    1,                 -- 1=临时表, 0=实际表
    'staging_table',   -- 中间表名（实际表模式时使用）
    0                  -- 0=实际执行, 1=测试模式
);
```

## SQL 使用示例

### 静默版（Java调用推荐）

```sql
-- 直接执行，无任何输出
CALL sp_cleanup_duplicate_records_silent(
    'orders', 'order_id', 'item_id', 'created_at',
    0, 'orders_staging', 0
);
```

### 标准版（调试用）

```sql
-- 测试模式：查看将被删除的数据
CALL sp_cleanup_duplicate_records(
    'orders', 'order_id', 'item_id', 'created_at',
    0, 'orders_preview', 1,
    @groups, @to_delete, @deleted
);
SELECT @groups, @to_delete, @deleted;

-- 查看中间表
SELECT * FROM orders_preview;

-- 确认后实际执行
CALL sp_cleanup_duplicate_records(
    'orders', 'order_id', 'item_id', 'created_at',
    0, 'orders_deleted', 0,
    @groups, @to_delete, @deleted
);
```

### 分步调用

```sql
-- 先获取待删除记录
CALL sp_get_duplicate_records_silent(
    'orders', 'order_id', 'item_id', 'created_at', 'my_staging'
);

-- 检查中间表内容
SELECT * FROM my_staging;

-- 确认后执行删除
CALL sp_delete_by_staging_silent(
    'orders', 'order_id', 'item_id', 'my_staging'
);
```

### 在其他存储过程中调用（动态表名 + 时间戳）

场景：已有存储过程，需要在特定条件下清理重复数据，表名由外部传入，中间表名使用动态表名+时间戳避免冲突。

```sql
DELIMITER $$

CREATE PROCEDURE sp_process_data_with_dedup(
    IN p_target_table VARCHAR(128),    -- 外部传入的动态表名
    IN p_need_dedup TINYINT            -- 是否需要去重
)
BEGIN
    DECLARE v_staging_table VARCHAR(200);
    DECLARE v_timestamp VARCHAR(20);

    -- 生成时间戳（精确到秒）
    SET v_timestamp = DATE_FORMAT(NOW(), '%Y%m%d%H%i%s');

    -- 拼接中间表名：动态表名 + 时间戳
    SET v_staging_table = CONCAT(p_target_table, '_dedup_', v_timestamp);

    -- ... 其他业务逻辑 ...

    -- 在条件判断中调用静默版去重
    IF p_need_dedup = 1 THEN
        -- 调用静默版，不会产生任何输出，不影响当前存储过程的结果集
        CALL sp_cleanup_duplicate_records_silent(
            p_target_table,      -- 动态表名
            'order_id',          -- 主键字段1（根据实际情况调整）
            'item_id',           -- 主键字段2
            'created_at',        -- 日期字段
            0,                   -- 使用实际表（保留中间表供检查）
            v_staging_table,     -- 动态生成的中间表名
            0                    -- 实际执行
        );
    END IF;

    -- ... 继续其他业务逻辑 ...

    -- 可选：清理中间表
    SET @sql_drop = CONCAT('DROP TABLE IF EXISTS ', v_staging_table);
    PREPARE stmt FROM @sql_drop;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

END$$

DELIMITER ;

-- 调用示例
CALL sp_process_data_with_dedup('orders', 1);
CALL sp_process_data_with_dedup('user_activities', 0);  -- 不去重
```

**完整示例：带动态字段名**

```sql
DELIMITER $$

CREATE PROCEDURE sp_batch_cleanup(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_date_field VARCHAR(128),
    IN p_batch_id VARCHAR(50)
)
BEGIN
    DECLARE v_staging VARCHAR(200);
    DECLARE v_record_count INT DEFAULT 0;

    -- 中间表名：表名_批次ID_时间戳
    SET v_staging = CONCAT(p_table_name, '_', p_batch_id, '_', UNIX_TIMESTAMP());

    -- 检查是否有重复数据（使用核心版获取统计信息）
    CALL sp_cleanup_duplicate_records_core(
        p_table_name, p_pk_field1, p_pk_field2, p_date_field,
        0, v_staging, 1,  -- dry_run=1 先测试
        @groups, @to_delete, @deleted, @staging_used
    );

    -- 根据重复数量决定是否执行
    IF @to_delete > 0 AND @to_delete < 10000 THEN
        -- 数量合理，执行实际删除
        CALL sp_cleanup_duplicate_records_silent(
            p_table_name, p_pk_field1, p_pk_field2, p_date_field,
            0, v_staging, 0  -- dry_run=0 实际执行
        );
    ELSEIF @to_delete >= 10000 THEN
        -- 数量过大，记录日志但不执行
        INSERT INTO cleanup_log (table_name, batch_id, pending_count, status, created_at)
        VALUES (p_table_name, p_batch_id, @to_delete, 'SKIPPED_TOO_MANY', NOW());
    END IF;

END$$

DELIMITER ;
```

## Java 调用示例

### 静默版（推荐，无需处理结果集）

```java
try (Connection conn = dataSource.getConnection()) {
    CallableStatement cs = conn.prepareCall(
        "{CALL sp_cleanup_duplicate_records_silent(?,?,?,?,?,?,?)}"
    );
    cs.setString(1, "orders");        // 表名
    cs.setString(2, "order_id");      // 主键字段1
    cs.setString(3, "item_id");       // 主键字段2
    cs.setString(4, "created_at");    // 日期字段
    cs.setInt(5, 0);                  // 0=实际表, 1=临时表
    cs.setString(6, "orders_staging"); // 中间表名
    cs.setInt(7, 0);                  // 0=实际执行, 1=测试模式
    cs.execute();
    // 无需处理任何结果集
}
```

### 需要统计信息时（使用核心版）

```java
try (Connection conn = dataSource.getConnection()) {
    CallableStatement cs = conn.prepareCall(
        "{CALL sp_cleanup_duplicate_records_core(?,?,?,?,?,?,?,?,?,?,?)}"
    );
    // IN参数
    cs.setString(1, "orders");
    cs.setString(2, "order_id");
    cs.setString(3, "item_id");
    cs.setString(4, "created_at");
    cs.setInt(5, 0);
    cs.setString(6, "orders_staging");
    cs.setInt(7, 0);
    // OUT参数
    cs.registerOutParameter(8, Types.INTEGER);   // duplicate_groups
    cs.registerOutParameter(9, Types.INTEGER);   // records_to_delete
    cs.registerOutParameter(10, Types.INTEGER);  // records_deleted
    cs.registerOutParameter(11, Types.VARCHAR);  // staging_table_used

    cs.execute();

    int groups = cs.getInt(8);
    int toDelete = cs.getInt(9);
    int deleted = cs.getInt(10);
    String stagingTable = cs.getString(11);
    System.out.printf("重复组: %d, 待删除: %d, 已删除: %d, 中间表: %s%n",
        groups, toDelete, deleted, stagingTable);
}
```

### MyBatis 调用

```xml
<!-- mapper.xml -->
<update id="cleanupDuplicates" statementType="CALLABLE">
    {CALL sp_cleanup_duplicate_records_silent(
        #{tableName}, #{pkField1}, #{pkField2}, #{dateField},
        #{useTempTable}, #{stagingTable}, #{dryRun}
    )}
</update>
```

```java
// Mapper接口
void cleanupDuplicates(@Param("tableName") String tableName,
                       @Param("pkField1") String pkField1,
                       @Param("pkField2") String pkField2,
                       @Param("dateField") String dateField,
                       @Param("useTempTable") int useTempTable,
                       @Param("stagingTable") String stagingTable,
                       @Param("dryRun") int dryRun);
```

## 快速测试

```bash
# 连接 MySQL
mysql -u root -p

# 执行测试
SOURCE test_setup.sql;
SOURCE sp_cleanup_duplicate_records.sql;
SOURCE test_run.sql;
```

## Docker 测试

```bash
# 启动 MySQL 5.7 容器
docker run -d --name mysql57 -e MYSQL_ROOT_PASSWORD=test123 -p 3306:3306 mysql:5.7

# 执行测试
docker exec -i mysql57 mysql -uroot -ptest123 < test_setup.sql
docker exec -i mysql57 mysql -uroot -ptest123 test_dedup < sp_cleanup_duplicate_records.sql
docker exec -i mysql57 mysql -uroot -ptest123 test_dedup < test_run.sql
```

## 架构说明

```
┌─────────────────────────────────────────────────────────────┐
│                      调用层                                  │
├─────────────────────┬───────────────────┬───────────────────┤
│ 标准版 (有输出)      │ 静默版 (无输出)    │ 直接调用核心      │
│ sp_cleanup_...      │ sp_cleanup_..._   │ sp_cleanup_..._   │
│                     │ silent            │ core              │
└─────────┬───────────┴─────────┬─────────┴─────────┬─────────┘
          │                     │                   │
          └─────────────────────┼───────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 核心版 (_core)                               │
│           包含所有业务逻辑，无任何SELECT输出                   │
│           通过OUT参数返回执行结果                             │
└─────────────────────────────────────────────────────────────┘
```
