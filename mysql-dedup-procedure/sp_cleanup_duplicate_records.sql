-- ============================================================================
-- MySQL 5.7 存储过程：清理重复记录（保留最新数据）
-- 功能：针对具有复合主键(2字段)和日期字段的表，删除重复的旧数据
-- 兼容：MySQL 5.7+
-- ============================================================================

DELIMITER $$

-- ============================================================================
-- 核心存储过程：清理重复记录（无任何SELECT输出）
-- 供其他版本调用，Java静默调用时使用
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_cleanup_duplicate_records_core$$

CREATE PROCEDURE sp_cleanup_duplicate_records_core(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_date_field VARCHAR(128),
    IN p_use_temp_table TINYINT,
    IN p_staging_table VARCHAR(128),
    IN p_dry_run TINYINT,
    OUT p_duplicate_groups INT,
    OUT p_records_to_delete INT,
    OUT p_records_deleted INT,
    OUT p_staging_table_used VARCHAR(128)
)
BEGIN
    DECLARE v_staging_table VARCHAR(128);

    -- 错误处理（静默版不输出错误信息，只回滚）
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
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
    SET p_staging_table_used = v_staging_table;

    -- Step 1: 查询重复组数量
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

    -- 如果没有重复数据，清理可能存在的旧中间表后返回
    IF p_duplicate_groups = 0 THEN
        IF p_use_temp_table = 0 THEN
            SET @sql_drop = CONCAT('DROP TABLE IF EXISTS ', v_staging_table);
            PREPARE stmt FROM @sql_drop;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
        END IF;
    ELSE
        -- Step 2: 创建中间表并筛选时间旧的数据
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

        -- Step 3: 根据中间表删除主表数据
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
        ELSE
            SET p_records_deleted = 0;
        END IF;
    END IF;
END$$

-- ============================================================================
-- 主存储过程：清理重复记录（带详细输出，用于调试和手动执行）
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_cleanup_duplicate_records$$

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
    DECLARE v_staging_table_used VARCHAR(128);

    -- 错误处理
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 @sqlstate = RETURNED_SQLSTATE, @errno = MYSQL_ERRNO, @text = MESSAGE_TEXT;
        SET @full_error = CONCAT('ERROR ', @errno, ' (', @sqlstate, '): ', @text);
        SELECT @full_error AS error_message;
        ROLLBACK;
    END;

    -- 调用核心过程
    CALL sp_cleanup_duplicate_records_core(
        p_table_name, p_pk_field1, p_pk_field2, p_date_field,
        p_use_temp_table, p_staging_table, p_dry_run,
        p_duplicate_groups, p_records_to_delete, p_records_deleted, v_staging_table_used
    );

    -- 输出步骤信息
    SELECT CONCAT('发现 ', p_duplicate_groups, ' 组重复数据（按 ', p_pk_field1, ' 分组）') AS step1_result;

    IF p_duplicate_groups = 0 THEN
        SELECT '没有发现重复数据，无需清理' AS result;
    ELSE
        SELECT CONCAT('已将 ', p_records_to_delete, ' 条旧记录放入中间表 ', v_staging_table_used) AS step2_result;

        -- 显示中间表内容（用于测试验证）
        SET @sql_show = CONCAT('SELECT * FROM ', v_staging_table_used, ' LIMIT 20');
        PREPARE stmt FROM @sql_show;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        IF p_dry_run = 0 THEN
            SELECT CONCAT('已从主表 ', p_table_name, ' 删除 ', p_records_deleted, ' 条记录') AS step3_result;
        ELSE
            SELECT CONCAT('【测试模式】将删除 ', p_records_to_delete, ' 条记录（未实际执行）') AS step3_result;
        END IF;

        IF p_use_temp_table = 0 THEN
            SELECT CONCAT('中间表 ', v_staging_table_used, ' 已保留，可用于验证或其他存储过程调用') AS cleanup_info;
        END IF;
    END IF;

    -- 返回汇总信息
    SELECT
        p_table_name AS target_table,
        p_duplicate_groups AS duplicate_groups,
        p_records_to_delete AS records_to_delete,
        p_records_deleted AS records_deleted,
        CASE WHEN p_dry_run = 1 THEN '测试模式' ELSE '已执行' END AS execution_mode,
        CASE WHEN p_use_temp_table = 1 THEN '临时表' ELSE v_staging_table_used END AS staging_table_type;
END$$

-- ============================================================================
-- 静默版：无任何输出，适合Java/程序调用
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_cleanup_duplicate_records_silent$$

CREATE PROCEDURE sp_cleanup_duplicate_records_silent(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_date_field VARCHAR(128),
    IN p_use_temp_table TINYINT,
    IN p_staging_table VARCHAR(128),
    IN p_dry_run TINYINT
)
BEGIN
    DECLARE v_dup_groups INT;
    DECLARE v_to_delete INT;
    DECLARE v_deleted INT;
    DECLARE v_staging_used VARCHAR(128);

    CALL sp_cleanup_duplicate_records_core(
        p_table_name, p_pk_field1, p_pk_field2, p_date_field,
        p_use_temp_table, p_staging_table, p_dry_run,
        v_dup_groups, v_to_delete, v_deleted, v_staging_used
    );
    -- 不输出任何结果
END$$

-- ============================================================================
-- 核心存储过程：获取待删除记录到中间表（无输出）
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_duplicate_records_core$$

CREATE PROCEDURE sp_get_duplicate_records_core(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_date_field VARCHAR(128),
    IN p_staging_table VARCHAR(128),
    OUT p_record_count INT,
    OUT p_staging_table_used VARCHAR(128)
)
BEGIN
    DECLARE v_staging_table VARCHAR(128);

    SET v_staging_table = IFNULL(p_staging_table, CONCAT(p_table_name, '_dedup_staging'));
    SET p_staging_table_used = v_staging_table;

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
END$$

-- ============================================================================
-- 辅助存储过程：获取待删除记录（带输出）
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
    DECLARE v_staging_table_used VARCHAR(128);

    CALL sp_get_duplicate_records_core(
        p_table_name, p_pk_field1, p_pk_field2, p_date_field,
        p_staging_table, p_record_count, v_staging_table_used
    );

    SELECT CONCAT('已创建中间表 ', v_staging_table_used, '，包含 ', p_record_count, ' 条待删除记录') AS result;
END$$

-- ============================================================================
-- 静默版：获取待删除记录（无输出）
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_duplicate_records_silent$$

CREATE PROCEDURE sp_get_duplicate_records_silent(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_date_field VARCHAR(128),
    IN p_staging_table VARCHAR(128)
)
BEGIN
    DECLARE v_record_count INT;
    DECLARE v_staging_used VARCHAR(128);

    CALL sp_get_duplicate_records_core(
        p_table_name, p_pk_field1, p_pk_field2, p_date_field,
        p_staging_table, v_record_count, v_staging_used
    );
    -- 不输出任何结果
END$$

-- ============================================================================
-- 核心存储过程：根据中间表删除主表数据（无输出）
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_delete_by_staging_core$$

CREATE PROCEDURE sp_delete_by_staging_core(
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
END$$

-- ============================================================================
-- 辅助存储过程：根据中间表删除（带输出）
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
    CALL sp_delete_by_staging_core(
        p_table_name, p_pk_field1, p_pk_field2,
        p_staging_table, p_deleted_count
    );

    SELECT CONCAT('已从 ', p_table_name, ' 删除 ', p_deleted_count, ' 条记录') AS result;
END$$

-- ============================================================================
-- 静默版：根据中间表删除（无输出）
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_delete_by_staging_silent$$

CREATE PROCEDURE sp_delete_by_staging_silent(
    IN p_table_name VARCHAR(128),
    IN p_pk_field1 VARCHAR(128),
    IN p_pk_field2 VARCHAR(128),
    IN p_staging_table VARCHAR(128)
)
BEGIN
    DECLARE v_deleted_count INT;

    CALL sp_delete_by_staging_core(
        p_table_name, p_pk_field1, p_pk_field2,
        p_staging_table, v_deleted_count
    );
    -- 不输出任何结果
END$$

DELIMITER ;
