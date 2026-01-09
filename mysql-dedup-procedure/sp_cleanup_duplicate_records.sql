-- ============================================================================
-- MySQL 5.7 存储过程：清理重复记录（保留最新数据）
-- 功能：针对具有复合主键(2字段)和日期字段的表，删除重复的旧数据
-- 兼容：MySQL 5.7+
-- ============================================================================

DELIMITER $$

-- 删除已存在的存储过程
DROP PROCEDURE IF EXISTS sp_cleanup_duplicate_records$$

-- ============================================================================
-- 主存储过程：清理重复记录
--
-- 参数说明：
--   p_table_name      - 目标表名
--   p_pk_field1       - 主键字段1（用于分组查找重复）
--   p_pk_field2       - 主键字段2
--   p_date_field      - 日期字段（用于判断新旧）
--   p_use_temp_table  - 是否使用临时表 (1=临时表, 0=实际表)
--   p_staging_table   - 中间表名称（仅当 p_use_temp_table=0 时使用）
--   p_dry_run         - 是否仅测试不实际删除 (1=测试, 0=实际执行)
--
-- 返回值：
--   通过 OUT 参数返回统计信息
-- ============================================================================
CREATE PROCEDURE sp_cleanup_duplicate_records(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_date_field VARCHAR(128),
    IN p_use_temp_table TINYINT,
    IN p_staging_table VARCHAR(128),
    IN p_dry_run TINYINT,
    OUT p_duplicate_groups INT,
    OUT p_records_to_delete INT,
    OUT p_records_deleted INT
)
BEGIN
    DECLARE v_staging_table VARCHAR(128);
    DECLARE v_sql TEXT;
    DECLARE v_count INT DEFAULT 0;

    -- 错误处理
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 @sqlstate = RETURNED_SQLSTATE, @errno = MYSQL_ERRNO, @text = MESSAGE_TEXT;
        SET @full_error = CONCAT('ERROR ', @errno, ' (', @sqlstate, '): ', @text);
        SELECT @full_error AS error_message;
        ROLLBACK;
    END;

    -- 初始化输出参数
    SET p_duplicate_groups = 0;
    SET p_records_to_delete = 0;
    SET p_records_deleted = 0;

    -- 确定中间表名称
    IF p_use_temp_table = 1 THEN
        SET v_staging_table = CONCAT('tmp_dedup_staging_', UNIX_TIMESTAMP());
    ELSE
        SET v_staging_table = IFNULL(p_staging_table, CONCAT(p_table_name, '_dedup_staging'));
    END IF;

    -- ========================================================================
    -- Step 1: 查询第一个主键字段中 GROUP BY 大于1的数量（找出重复组）
    -- ========================================================================
    SET @sql_count_groups = CONCAT(
        'SELECT COUNT(*) INTO @dup_groups FROM (',
        '  SELECT ', p_pk_field1, ' ',
        '  FROM ', p_table_name, ' ',
        '  GROUP BY ', p_pk_field1, ' ',
        '  HAVING COUNT(*) > 1',
        ') AS dup_check'
    );

    PREPARE stmt FROM @sql_count_groups;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET p_duplicate_groups = @dup_groups;

    SELECT CONCAT('发现 ', p_duplicate_groups, ' 组重复数据（按 ', p_pk_field1, ' 分组）') AS step1_result;

    -- 如果没有重复数据，直接返回
    IF p_duplicate_groups = 0 THEN
        SELECT '没有发现重复数据，无需清理' AS result;
        -- 清理可能存在的旧中间表（如果是实际表模式）
        IF p_use_temp_table = 0 THEN
            SET @sql_drop = CONCAT('DROP TABLE IF EXISTS ', v_staging_table);
            PREPARE stmt FROM @sql_drop;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
        END IF;
        -- 返回，不继续执行
    ELSE
        -- ====================================================================
        -- Step 2: 创建中间表并筛选时间旧的数据
        -- ====================================================================

        -- 删除旧的中间表（如果存在）
        IF p_use_temp_table = 1 THEN
            SET @sql_create = CONCAT(
                'CREATE TEMPORARY TABLE ', v_staging_table, ' AS ',
                'SELECT t1.', p_pk_field1, ', t1.', p_pk_field2, ', t1.', p_date_field, ' ',
                'FROM ', p_table_name, ' t1 ',
                'INNER JOIN (',
                '  SELECT ', p_pk_field1, ', MAX(', p_date_field, ') AS max_date ',
                '  FROM ', p_table_name, ' ',
                '  GROUP BY ', p_pk_field1, ' ',
                '  HAVING COUNT(*) > 1',
                ') t2 ON t1.', p_pk_field1, ' = t2.', p_pk_field1, ' ',
                'WHERE t1.', p_date_field, ' < t2.max_date'
            );
        ELSE
            -- 先删除旧表
            SET @sql_drop = CONCAT('DROP TABLE IF EXISTS ', v_staging_table);
            PREPARE stmt FROM @sql_drop;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;

            SET @sql_create = CONCAT(
                'CREATE TABLE ', v_staging_table, ' AS ',
                'SELECT t1.', p_pk_field1, ', t1.', p_pk_field2, ', t1.', p_date_field, ' ',
                'FROM ', p_table_name, ' t1 ',
                'INNER JOIN (',
                '  SELECT ', p_pk_field1, ', MAX(', p_date_field, ') AS max_date ',
                '  FROM ', p_table_name, ' ',
                '  GROUP BY ', p_pk_field1, ' ',
                '  HAVING COUNT(*) > 1',
                ') t2 ON t1.', p_pk_field1, ' = t2.', p_pk_field1, ' ',
                'WHERE t1.', p_date_field, ' < t2.max_date'
            );
        END IF;

        PREPARE stmt FROM @sql_create;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        -- 统计待删除记录数
        SET @sql_count_staging = CONCAT('SELECT COUNT(*) INTO @staging_count FROM ', v_staging_table);
        PREPARE stmt FROM @sql_count_staging;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        SET p_records_to_delete = @staging_count;

        SELECT CONCAT('已将 ', p_records_to_delete, ' 条旧记录放入中间表 ', v_staging_table) AS step2_result;

        -- 显示中间表内容（用于测试验证）
        SET @sql_show = CONCAT('SELECT * FROM ', v_staging_table, ' LIMIT 20');
        PREPARE stmt FROM @sql_show;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        -- ====================================================================
        -- Step 3: 根据中间表删除主表数据
        -- ====================================================================
        IF p_dry_run = 0 THEN
            START TRANSACTION;

            SET @sql_delete = CONCAT(
                'DELETE t FROM ', p_table_name, ' t ',
                'INNER JOIN ', v_staging_table, ' s ',
                'ON t.', p_pk_field1, ' = s.', p_pk_field1, ' ',
                'AND t.', p_pk_field2, ' = s.', p_pk_field2
            );

            PREPARE stmt FROM @sql_delete;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;

            SET p_records_deleted = ROW_COUNT();

            COMMIT;

            SELECT CONCAT('已从主表 ', p_table_name, ' 删除 ', p_records_deleted, ' 条记录') AS step3_result;
        ELSE
            SET p_records_deleted = 0;
            SELECT CONCAT('【测试模式】将删除 ', p_records_to_delete, ' 条记录（未实际执行）') AS step3_result;
        END IF;

        -- 如果使用临时表，会自动清理；如果是实际表，保留供检查
        IF p_use_temp_table = 0 THEN
            SELECT CONCAT('中间表 ', v_staging_table, ' 已保留，可用于验证或其他存储过程调用') AS cleanup_info;
        END IF;
    END IF;

    -- 返回汇总信息
    SELECT
        p_table_name AS target_table,
        p_duplicate_groups AS duplicate_groups,
        p_records_to_delete AS records_to_delete,
        p_records_deleted AS records_deleted,
        CASE WHEN p_dry_run = 1 THEN '测试模式' ELSE '已执行' END AS execution_mode,
        CASE WHEN p_use_temp_table = 1 THEN '临时表' ELSE v_staging_table END AS staging_table_type
    AS summary;

END$$

-- ============================================================================
-- 辅助存储过程：仅获取待删除记录到中间表（供其他存储过程调用）
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_duplicate_records$$

CREATE PROCEDURE sp_get_duplicate_records(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_date_field VARCHAR(128),
    IN p_staging_table VARCHAR(128),
    OUT p_record_count INT
)
BEGIN
    DECLARE v_staging_table VARCHAR(128);

    SET v_staging_table = IFNULL(p_staging_table, CONCAT(p_table_name, '_dedup_staging'));

    -- 删除旧表
    SET @sql_drop = CONCAT('DROP TABLE IF EXISTS ', v_staging_table);
    PREPARE stmt FROM @sql_drop;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- 创建中间表
    SET @sql_create = CONCAT(
        'CREATE TABLE ', v_staging_table, ' AS ',
        'SELECT t1.* ',
        'FROM ', p_table_name, ' t1 ',
        'INNER JOIN (',
        '  SELECT ', p_pk_field1, ', MAX(', p_date_field, ') AS max_date ',
        '  FROM ', p_table_name, ' ',
        '  GROUP BY ', p_pk_field1, ' ',
        '  HAVING COUNT(*) > 1',
        ') t2 ON t1.', p_pk_field1, ' = t2.', p_pk_field1, ' ',
        'WHERE t1.', p_date_field, ' < t2.max_date'
    );

    PREPARE stmt FROM @sql_create;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- 获取记录数
    SET @sql_count = CONCAT('SELECT COUNT(*) INTO @cnt FROM ', v_staging_table);
    PREPARE stmt FROM @sql_count;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET p_record_count = @cnt;

    SELECT CONCAT('已创建中间表 ', v_staging_table, '，包含 ', p_record_count, ' 条待删除记录') AS result;
END$$

-- ============================================================================
-- 辅助存储过程：根据中间表删除主表数据
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_delete_by_staging$$

CREATE PROCEDURE sp_delete_by_staging(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_staging_table VARCHAR(128),
    OUT p_deleted_count INT
)
BEGIN
    -- 执行删除
    SET @sql_delete = CONCAT(
        'DELETE t FROM ', p_table_name, ' t ',
        'INNER JOIN ', p_staging_table, ' s ',
        'ON t.', p_pk_field1, ' = s.', p_pk_field1, ' ',
        'AND t.', p_pk_field2, ' = s.', p_pk_field2
    );

    PREPARE stmt FROM @sql_delete;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET p_deleted_count = ROW_COUNT();

    SELECT CONCAT('已从 ', p_table_name, ' 删除 ', p_deleted_count, ' 条记录') AS result;
END$$

DELIMITER ;
