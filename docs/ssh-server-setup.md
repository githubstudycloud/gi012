# SSH服务器配置文档

## 服务器信息

### 基本信息
- **主机名**: ubuntu
- **IP地址**: 192.168.0.122
- **操作系统**: Ubuntu 22.04.5 LTS (Jammy Jellyfish)
- **内核版本**: Linux 5.15.0-119-generic
- **架构**: x86_64

### 硬件配置
- **CPU型号**: AMD Ryzen 5 5625U with Radeon Graphics
- **CPU核心数**: 6核
- **线程数**: 6 (每核1线程)
- **内存**: 16GB (15Gi total, 15Gi available)
- **交换空间**: 4GB
- **磁盘空间**: 391GB总容量，已使用7.6GB (3%)，可用364GB

### 用户信息
- **当前用户**: ubuntu (uid=1000, gid=1000)
- **用户组**: ubuntu, adm, cdrom, sudo, dip, plugdev, lxd

---

## 配置操作记录

### 1. 硬件信息检测

**执行命令**:
```bash
uname -a && cat /etc/os-release && lscpu | grep -E "^(Architecture|CPU\(s\)|Model name|Thread\(s\) per core|Core\(s\) per socket)" && free -h && df -h / && hostname -I
```

**执行时间**: 2025-12-30
**状态**: ✅ 完成

---

### 2. 设置用户密码

**目标**: 设置ubuntu用户密码为 `12345678`

**一句话命令** (需要root权限):
```bash
echo "ubuntu:12345678" | sudo chpasswd && echo "密码设置成功"
```

**替代方案** (如果当前用户有sudo权限):
```bash
# 方法1: 使用chpasswd (推荐)
echo "ubuntu:12345678" | sudo chpasswd

# 方法2: 使用passwd
echo -e "12345678\n12345678" | sudo passwd ubuntu
```

**注意事项**:
- 需要当前用户具有sudo权限
- 如果是修改当前用户密码，使用`passwd`命令需要先输入旧密码
- 建议在生产环境使用更强的密码

**状态**: ⚠️ 需要手动执行（需要sudo密码）

---

### 3. 配置免密sudo权限

**目标**: 为ubuntu用户配置免密码sudo权限

**一句话命令**:
```bash
echo "ubuntu ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ubuntu && sudo chmod 440 /etc/sudoers.d/ubuntu && echo "免密sudo配置成功"
```

**详细步骤**:
1. 创建sudoers配置文件
2. 设置正确的权限 (440)
3. 验证配置

**验证命令**:
```bash
sudo -n true && echo "免密sudo已启用" || echo "免密sudo未启用"
```

**安全建议**:
- 仅在开发/测试环境使用免密sudo
- 生产环境建议保留密码验证
- 可以限制免密sudo的命令范围

**状态**: ⚠️ 需要手动执行（需要sudo密码）

---

### 4. SSH服务安装与配置

**检测命令**:
```bash
dpkg -l | grep openssh-server && systemctl status ssh --no-pager
```

**检测结果**:
- ✅ OpenSSH Server已安装 (版本: 1:8.9p1-3ubuntu0.10)
- ✅ SSH服务正在运行 (Active: active (running))
- ✅ SSH服务已设置开机自启动 (enabled)
- ✅ 监听端口: 22 (IPv4和IPv6)
- ✅ 服务启动时间: 2025-12-29 23:22:11 UTC
- ✅ 当前连接: 已有来自192.168.0.116的活跃连接

**安装命令** (如果未安装):
```bash
sudo apt update && sudo apt install -y openssh-server && sudo systemctl enable --now ssh && echo "SSH安装并启动成功"
```

**常用管理命令**:
```bash
# 启动SSH服务
sudo systemctl start ssh

# 停止SSH服务
sudo systemctl stop ssh

# 重启SSH服务
sudo systemctl restart ssh

# 查看SSH服务状态
sudo systemctl status ssh

# 设置开机自启动
sudo systemctl enable ssh

# 禁用开机自启动
sudo systemctl disable ssh
```

**状态**: ✅ 已完成（服务已安装并运行）

---

## 快速配置脚本

以下是完整的一句话配置命令（需要sudo权限）:

```bash
# 完整配置 (设置密码 + 免密sudo + 安装SSH)
echo "ubuntu:12345678" | sudo chpasswd && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ubuntu && sudo chmod 440 /etc/sudoers.d/ubuntu && sudo apt update && sudo apt install -y openssh-server && sudo systemctl enable --now ssh && echo "所有配置完成" || echo "配置过程中出现错误"
```

**分步执行**:
```bash
# 步骤1: 设置密码
echo "ubuntu:12345678" | sudo chpasswd

# 步骤2: 配置免密sudo
echo "ubuntu ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ubuntu && sudo chmod 440 /etc/sudoers.d/ubuntu

# 步骤3: 安装并启动SSH (如果未安装)
sudo apt update && sudo apt install -y openssh-server && sudo systemctl enable --now ssh
```

---

## 安全建议

1. **密码强度**:
   - 示例密码`12345678`仅用于测试
   - 生产环境建议使用16位以上强密码
   - 包含大小写字母、数字和特殊字符

2. **SSH安全加固**:
   ```bash
   # 禁用root登录
   sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

   # 修改SSH端口 (可选)
   sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

   # 禁用密码登录，仅使用密钥 (可选)
   sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

   # 重启SSH服务应用配置
   sudo systemctl restart ssh
   ```

3. **防火墙配置**:
   ```bash
   # 安装UFW防火墙
   sudo apt install -y ufw

   # 允许SSH连接
   sudo ufw allow 22/tcp

   # 启用防火墙
   sudo ufw enable
   ```

4. **免密sudo风险**:
   - 仅在信任环境使用
   - 考虑限制特定命令的免密执行
   - 定期审计sudo日志

---

## 故障排查

### SSH无法连接
```bash
# 检查SSH服务状态
sudo systemctl status ssh

# 检查SSH端口监听
sudo netstat -tulpn | grep :22

# 检查防火墙规则
sudo ufw status

# 查看SSH日志
sudo tail -f /var/log/auth.log
```

### sudo需要密码
```bash
# 检查sudoers配置
sudo cat /etc/sudoers.d/ubuntu

# 验证文件权限
ls -l /etc/sudoers.d/ubuntu

# 测试免密sudo
sudo -n true && echo "OK" || echo "需要密码"
```

---

## 文档更新记录

| 日期 | 操作 | 状态 |
|------|------|------|
| 2025-12-30 | 初始化文档，记录硬件信息 | ✅ |
| 2025-12-30 | 检测SSH服务状态 | ✅ |
| 2025-12-30 | 提供密码设置和免密sudo配置方案 | 📝 |

---

## 附录

### 系统完整信息
```
Linux ubuntu 5.15.0-119-generic #129-Ubuntu SMP Fri Aug 2 19:25:20 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux

PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
```

### 联系信息
- 服务器管理员: ubuntu@192.168.0.122
- 文档维护: 自动生成于2025-12-30
