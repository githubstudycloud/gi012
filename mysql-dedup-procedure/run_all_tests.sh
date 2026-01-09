#!/bin/bash
# ============================================================================
# MySQL 5.7 存储过程完整测试脚本
# 使用方法: ./run_all_tests.sh [mysql_host] [mysql_user] [mysql_password]
# ============================================================================

MYSQL_HOST="${1:-localhost}"
MYSQL_USER="${2:-root}"
MYSQL_PASS="${3:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}MySQL 重复数据清理存储过程 - 测试套件${NC}"
echo -e "${YELLOW}============================================${NC}"

# 构建MySQL命令
if [ -z "$MYSQL_PASS" ]; then
    MYSQL_CMD="mysql -h $MYSQL_HOST -u $MYSQL_USER"
else
    MYSQL_CMD="mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASS"
fi

# 检查MySQL连接
echo -e "\n${YELLOW}[1/4] 检查MySQL连接...${NC}"
if $MYSQL_CMD -e "SELECT VERSION();" 2>/dev/null | grep -q "5.7"; then
    echo -e "${GREEN}✓ MySQL 5.7 连接成功${NC}"
elif $MYSQL_CMD -e "SELECT VERSION();" 2>/dev/null; then
    MYSQL_VER=$($MYSQL_CMD -e "SELECT VERSION();" 2>/dev/null | tail -1)
    echo -e "${YELLOW}⚠ MySQL版本: $MYSQL_VER (推荐5.7)${NC}"
else
    echo -e "${RED}✗ MySQL连接失败${NC}"
    echo "请检查MySQL服务是否运行，或提供正确的连接参数"
    exit 1
fi

# 执行测试设置
echo -e "\n${YELLOW}[2/4] 创建测试数据库和测试数据...${NC}"
if $MYSQL_CMD < test_setup.sql 2>/dev/null; then
    echo -e "${GREEN}✓ 测试数据创建成功${NC}"
else
    echo -e "${RED}✗ 测试数据创建失败${NC}"
    exit 1
fi

# 加载存储过程
echo -e "\n${YELLOW}[3/4] 加载存储过程...${NC}"
if $MYSQL_CMD test_dedup < sp_cleanup_duplicate_records.sql 2>/dev/null; then
    echo -e "${GREEN}✓ 存储过程加载成功${NC}"
else
    echo -e "${RED}✗ 存储过程加载失败${NC}"
    exit 1
fi

# 执行测试
echo -e "\n${YELLOW}[4/4] 执行测试用例...${NC}"
if $MYSQL_CMD test_dedup < test_run.sql 2>/dev/null; then
    echo -e "${GREEN}✓ 所有测试执行完成${NC}"
else
    echo -e "${RED}✗ 测试执行出错${NC}"
    exit 1
fi

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}所有测试通过!${NC}"
echo -e "${GREEN}============================================${NC}"

# 清理选项
read -p "是否删除测试数据库 test_dedup? (y/N): " cleanup
if [ "$cleanup" = "y" ] || [ "$cleanup" = "Y" ]; then
    $MYSQL_CMD -e "DROP DATABASE IF EXISTS test_dedup;"
    echo -e "${GREEN}测试数据库已清理${NC}"
fi
