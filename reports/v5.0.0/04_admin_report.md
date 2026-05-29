# ClawsJoy v5.0.0 - 系统运维报告

## 部署架构
┌─────────────────────────────────────────────────────────────┐
│ 负载均衡 (可选) │
├─────────────────────────────────────────────────────────────┤
│ gunicorn (2 workers + gevent) │
│ │ │
│ ┌────────────┴────────────┐ │
│ ▼ ▼ │
│ Flask App Ollama │
│ (主网关) (LLM服务) │
│ │ │ │
│ └────────────┬────────────┘ │
│ ▼ │
│ ChromaDB (向量库) │
└─────────────────────────────────────────────────────────────┘

## 启动命令

```bash
# 生产启动
./start_prod.sh

# 停止服务
./stop_all.sh

# 状态检查
./status_prod.sh
##配置热重载
所有配置在 config/ 目录下，修改后重启服务生效。

##监控指标
##端点	说明
/api/health	健康检查
/metrics	Prometheus 指标
/api/closed_loop/status	闭环状态
/api/agents/health	Agent 健康
##日志管理
# 查看错误日志
tail -f logs/error.log

# 查看访问日志
tail -f logs/access.log

# 日志轮转
cat /etc/logrotate.d/clawsjoy
##备份策略
# 自动备份每天3点执行
crontab -l | grep backup
##资源要求
资源	最低	推荐
CPU	2核	4核
内存	4GB	8GB
磁盘	10GB	20GB
GPU	无	6GB+ (Ollama)
##故障恢复
# 快速重启
./stop_all.sh && ./start_all.sh

# 从稳定版本恢复
cp -r stable_release/clawsjoy_v5.0.0_*/* .

