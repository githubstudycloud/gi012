# MySQL 5.7 重复数据清理存储过程

清理具有复合主键和日期字段的表中的重复数据，保留最新记录。

## 功能特性

- 支持任意表名、字段名的动态处理
- 支持临时表和实际表两种中间表模式
- 支持测试模式（dry run）和实际执行模式
- 提供辅助存储过程，便于分步调用
- 提供简化版存储过程（无OUT参数），便于Java等程序调用
- MySQL 5.7 完全兼容

## 文件说明

| 文件 | 说明 |
|------|------|
| `sp_cleanup_duplicate_records.sql` | 主存储过程定义 |
| `test_setup.sql` | 测试数据库和测试数据 |
| `test_run.sql` | 测试执行脚本 |

## 存储过程列表

| 存储过程 | 说明 | OUT参数 |
|---------|------|---------|
| `sp_cleanup_duplicate_records` | 主过程：完整清理流程 | 有 |
| `sp_cleanup_duplicate_records_simple` | 主过程简化版 | 无 |
| `sp_get_duplicate_records` | 辅助：获取重复记录到中间表 | 有 |
| `sp_get_duplicate_records_simple` | 辅助简化版 | 无 |
| `sp_delete_by_staging` | 辅助：根据中间表删除 | 有 |
| `sp_delete_by_staging_simple` | 辅助简化版 | 无 |

## 存储过程详细说明

### `sp_cleanup_duplicate_records` / `sp_cleanup_duplicate_records_simple`

主存储过程，完成完整的重复数据清理流程。

```sql
-- 完整版（带OUT参数）
CALL sp_cleanup_duplicate_records(
    'table_name',      -- 目标表名
    'pk_field1',       -- 主键字段1（用于分组）
    'pk_field2',       -- 主键字段2
    'date_field',      -- 日期字段
    1,                 -- 1=临时表, 0=实际表
    'staging_table',   -- 中间表名（实际表模式）
    1,                 -- 1=测试模式, 0=实际执行
    @groups, @to_delete, @deleted  -- 输出参数
);

-- 简化版（无OUT参数，推荐Java调用）
CALL sp_cleanup_duplicate_records_simple(
    'table_name', 'pk_field1', 'pk_field2', 'date_field',
    1, 'staging_table', 1
);
```

### `sp_get_duplicate_records` / `sp_get_duplicate_records_simple`

获取待删除记录到中间表，供其他存储过程调用。

```sql
-- 完整版
CALL sp_get_duplicate_records(
    'table_name', 'pk_field1', 'pk_field2', 'date_field',
    'staging_table', @record_count
);

-- 简化版
CALL sp_get_duplicate_records_simple(
    'table_name', 'pk_field1', 'pk_field2', 'date_field',
    'staging_table'
);
```

### `sp_delete_by_staging` / `sp_delete_by_staging_simple`

根据中间表删除主表数据。

```sql
-- 完整版
CALL sp_delete_by_staging(
    'table_name', 'pk_field1', 'pk_field2',
    'staging_table', @deleted_count
);

-- 简化版
CALL sp_delete_by_staging_simple(
    'table_name', 'pk_field1', 'pk_field2', 'staging_table'
);
```

## SQL 使用示例

```sql
-- 1. 测试模式查看将被删除的数据
CALL sp_cleanup_duplicate_records_simple(
    'orders', 'order_id', 'item_id', 'created_at',
    0, 'orders_preview', 1
);
SELECT * FROM orders_preview;

-- 2. 确认无误后实际执行
CALL sp_cleanup_duplicate_records_simple(
    'orders', 'order_id', 'item_id', 'created_at',
    0, 'orders_deleted', 0
);

-- 3. 分步调用（先获取再删除）
CALL sp_get_duplicate_records_simple(
    'orders', 'order_id', 'item_id', 'created_at', 'my_staging'
);
-- 检查 my_staging 表内容
SELECT * FROM my_staging;
CALL sp_delete_by_staging_simple(
    'orders', 'order_id', 'item_id', 'my_staging'
);
```

## Java 调用示例

### 使用简化版（推荐）

```java
// 无需处理OUT参数，直接调用
try (Connection conn = dataSource.getConnection()) {
    CallableStatement cs = conn.prepareCall(
        "{CALL sp_cleanup_duplicate_records_simple(?,?,?,?,?,?,?)}"
    );
    cs.setString(1, "orders");        // 表名
    cs.setString(2, "order_id");      // 主键字段1
    cs.setString(3, "item_id");       // 主键字段2
    cs.setString(4, "created_at");    // 日期字段
    cs.setInt(5, 0);                  // 0=实际表, 1=临时表
    cs.setString(6, "orders_staging"); // 中间表名
    cs.setInt(7, 0);                  // 0=实际执行, 1=测试模式
    cs.execute();
}
```

### 使用完整版（需要获取统计信息时）

```java
try (Connection conn = dataSource.getConnection()) {
    CallableStatement cs = conn.prepareCall(
        "{CALL sp_cleanup_duplicate_records(?,?,?,?,?,?,?,?,?,?)}"
    );
    // 设置IN参数
    cs.setString(1, "orders");
    cs.setString(2, "order_id");
    cs.setString(3, "item_id");
    cs.setString(4, "created_at");
    cs.setInt(5, 0);
    cs.setString(6, "orders_staging");
    cs.setInt(7, 0);
    // 注册OUT参数
    cs.registerOutParameter(8, Types.INTEGER);   // duplicate_groups
    cs.registerOutParameter(9, Types.INTEGER);   // records_to_delete
    cs.registerOutParameter(10, Types.INTEGER);  // records_deleted

    cs.execute();

    // 获取统计信息
    int groups = cs.getInt(8);
    int toDelete = cs.getInt(9);
    int deleted = cs.getInt(10);
    System.out.printf("重复组: %d, 待删除: %d, 已删除: %d%n", groups, toDelete, deleted);
}
```

### MyBatis 调用

```xml
<!-- mapper.xml -->
<select id="cleanupDuplicates" statementType="CALLABLE">
    {CALL sp_cleanup_duplicate_records_simple(
        #{tableName}, #{pkField1}, #{pkField2}, #{dateField},
        #{useTempTable}, #{stagingTable}, #{dryRun}
    )}
</select>
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
