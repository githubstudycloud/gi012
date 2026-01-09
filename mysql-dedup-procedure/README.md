# MySQL 5.7 重复数据清理存储过程

清理具有复合主键和日期字段的表中的重复数据，保留最新记录。

## 功能特性

- 支持任意表名、字段名的动态处理
- 支持临时表和实际表两种中间表模式
- 支持测试模式（dry run）和实际执行模式
- 提供辅助存储过程，便于分步调用
- MySQL 5.7 完全兼容

## 文件说明

| 文件 | 说明 |
|------|------|
| `sp_cleanup_duplicate_records.sql` | 主存储过程定义 |
| `test_setup.sql` | 测试数据库和测试数据 |
| `test_run.sql` | 测试执行脚本 |

## 存储过程说明

### `sp_cleanup_duplicate_records`

主存储过程，完成完整的重复数据清理流程。

```sql
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
```

### `sp_get_duplicate_records`

获取待删除记录到中间表，供其他存储过程调用。

```sql
CALL sp_get_duplicate_records(
    'table_name',
    'pk_field1',
    'pk_field2',
    'date_field',
    'staging_table',
    @record_count
);
```

### `sp_delete_by_staging`

根据中间表删除主表数据。

```sql
CALL sp_delete_by_staging(
    'table_name',
    'pk_field1',
    'pk_field2',
    'staging_table',
    @deleted_count
);
```

## 使用示例

```sql
-- 1. 测试模式查看将被删除的数据
CALL sp_cleanup_duplicate_records(
    'orders', 'order_id', 'item_id', 'created_at',
    0, 'orders_preview', 1,
    @g, @t, @d
);
SELECT * FROM orders_preview;

-- 2. 确认无误后实际执行
CALL sp_cleanup_duplicate_records(
    'orders', 'order_id', 'item_id', 'created_at',
    0, 'orders_deleted', 0,
    @g, @t, @d
);

-- 3. 分步调用（先获取再删除）
CALL sp_get_duplicate_records(
    'orders', 'order_id', 'item_id', 'created_at',
    'my_staging', @cnt
);
-- 检查 my_staging 表内容
CALL sp_delete_by_staging(
    'orders', 'order_id', 'item_id', 'my_staging', @deleted
);
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
