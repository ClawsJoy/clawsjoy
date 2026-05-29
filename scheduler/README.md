# ClawsJoy 调度系统

## 目录结构
scheduler/
├── trigger.sh # 主触发脚本（入口）
├── gpu_manager.py # GPU 资源管理器
├── gpu_task.sh # GPU 任务提交器
├── reliable_scheduler.py # 可靠调度器（带持久化）
├── daemon.sh # 守护进程脚本
└── archive/ # 归档的旧脚本

## 调度架构

### 触发机制
- `trigger.sh` - 主触发脚本，由 cron 调用
- `reliable_scheduler.py` - Python 实现，支持任务持久化和恢复

### GPU 调度
- `gpu_manager.py` - 管理 GPU 资源，避免显存冲突
- `gpu_task.sh` - 提交 GPU 密集型任务（视频合成、AI 生图）

### 守护进程
- `daemon.sh` - 保持调度器持续运行

## 配置

### Cron 配置示例
```bash
# 每小时执行一次
0 * * * * /path/to/scheduler/trigger.sh

# 每天凌晨清理
0 3 * * * /path/to/scheduler/cleanup.sh
#调度器配置
config/scheduler_config.json - 调度器参数

config/crontab_config.txt - Crontab 模板

#数据文件
#相关模块
#智能调度器 (core/lib/smart_scheduler.py)
#基于成功预测的动态调度

#任务优先级动态调整

#任务队列 (core/lib/task_queue.py)
#支持优先级队列

#任务持久化

#主动服务 (core/lib/smart_active_loop.py)
#每小时主动检查

#维护任务执行

#清理历史
2026-05-29: 归档冗余脚本

gpu_cpu_trigger.sh (功能合并到 gpu_manager.py)

gpu_optimized.sh (功能合并到 gpu_manager.py)

smart_trigger.sh (功能合并到 trigger.sh)

submit_gpu_task.sh (功能合并到 gpu_task.sh)
