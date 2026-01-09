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
