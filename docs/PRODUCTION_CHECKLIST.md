# ClawsJoy 4.0 生产环境部署检查清单

## 部署前检查

### 1. 环境准备
- [ ] Python 3.13+ 已安装
- [ ] 8GB+ RAM 可用
- [ ] 10GB+ 磁盘空间
- [ ] Linux/macOS/Windows WSL2 环境

### 2. 依赖服务
- [ ] Ollama 已安装并运行 (`ollama serve`)
- [ ] 至少一个 LLM 模型已下载 (`ollama pull qwen2.5:7b`)
- [ ] ComfyUI 已安装（可选，图像生成需要）
- [ ] 端口 5443-5446 未被占用

### 3. 配置检查
- [ ] `config/driver/*.yaml` 已按生产环境调整
- [ ] JWT_SECRET 已修改为强密码
- [ ] SSL 证书已配置（生产环境用 CA 签发）
- [ ] `.env` 文件已配置

### 4. 安全配置
- [ ] 默认密码已修改（user1/admin123）
- [ ] 敏感信息已脱敏配置
- [ ] HTTPS 已启用
- [ ] 防火墙规则已配置

## 部署执行

### 5. 启动服务
```bash
# 方式一：本地启动
./start_all.sh

# 方式二：Docker 启动
docker-compose up -d
6. 验证服务
# 健康检查
curl -k https://localhost:5443/health
curl -k https://localhost:5444/auth/verify
curl -k https://localhost:5445/
curl -k https://localhost:5446/

# 登录测试
curl -k -X POST https://localhost:5444/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "password": "admin123"}'
部署后验证
7. 功能测试
用户登录成功

智能对话响应正常

图像生成功能正常（如配置）

用户偏好保存/加载正常

Agent 心跳正常

看门狗监控正常

8. 性能测试
并发用户数: _____

平均响应时间: _____ms

CPU 使用率: _____%

内存使用率: _____%

9. 稳定性测试
7x24 小时运行测试

内存泄漏检查

日志轮转配置

应急预案
10. 备份策略
数据自动备份已配置

配置文件已备份

备份恢复演练已完成

11. 监控告警
服务监控已配置

告警通知已设置

日志收集已配置

12. 灾难恢复
恢复步骤已文档化

恢复演练已完成

签字确认
部署人: _____________

验证人: _____________

日期: _____________

版本: ClawsJoy 4.0.0

