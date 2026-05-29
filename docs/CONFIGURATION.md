# ClawsJoy 配置文档

**生成时间**: 2026-05-18 23:42:58
**配置文件**: `config/driver/unified.yaml`

## 配置说明


### services

### services.ports
- `services.ports.gateway`: 5002
- `services.ports.file`: 5003
- `services.ports.multi_agent`: 5005
- `services.ports.doc`: 5008
- `services.ports.agent_api`: 5010
- `services.ports.web`: 5011
- `services.ports.registry`: 5022
- `services.ports.scheduler`: 5023
- `services.ports.skill_market`: 5024
- `services.ports.promo`: 8105
- `services.ports.chat`: 8101
- `services.ports.joymate`: 8093
- `services.ports.tts`: 9000
- `services.ports.meilisearch`: 7700
- `services.ports.qdrant`: 6333

### services.hosts
- `services.hosts.internal`: smart_config.HOST
- `services.hosts.external`: 0.0.0.0

### services.urls
- `services.urls.immd`: https://www.immd.gov.hk/hks/services/index.html
- `services.urls.info_gov`: https://www.info.gov.hk/gia/general/today.htm
- `services.urls.unsplash_api`: https://api.unsplash.com/search/photos

### llm

### llm.ollama
- `llm.ollama.host`: 127.0.0.1
- `llm.ollama.port`: 11434
- `llm.ollama.model`: qwen2.5:3b
- `llm.ollama.timeout`: 30
- `llm.ollama.temperature`: 0.7
- `llm.ollama.max_tokens`: 2000
- `llm.alternatives`: [{'model': 'qwen2.5:7b', 'timeout': 60}, {'model': 'llama3.2:3b', 'timeout': 45}]

### thresholds

### thresholds.success_rate
- `thresholds.success_rate.high`: 0.9
- `thresholds.success_rate.medium`: 0.7
- `thresholds.success_rate.low`: 0.5
- `thresholds.success_rate.critical`: 0.3

### thresholds.quality
- `thresholds.quality.excellent`: 0.8
- `thresholds.quality.good`: 0.5
- `thresholds.quality.poor`: 0.3

### thresholds.resource
- `thresholds.resource.cpu_warning`: 80
- `thresholds.resource.cpu_critical`: 90
- `thresholds.resource.memory_warning`: 80
- `thresholds.resource.memory_critical`: 90
- `thresholds.resource.disk_warning`: 85
- `thresholds.resource.disk_critical`: 95

### timing

### timing.intervals
- `timing.intervals.health_check`: 30
- `timing.intervals.heartbeat`: 30
- `timing.intervals.auto_heal`: 600
- `timing.intervals.dream_cycle`: 300
- `timing.intervals.reflection`: 60

### timing.timeouts
- `timing.timeouts.http`: 30
- `timing.timeouts.llm`: 60
- `timing.timeouts.long_llm`: 90

### timing.delays
- `timing.delays.retry`: 2
- `timing.delays.cooldown`: 5

### limits

### limits.queues
- `limits.queues.event_queue`: 500
- `limits.queues.message_history`: 100
- `limits.queues.retry_max`: 3

### limits.memories
- `limits.memories.short_term`: 20
- `limits.memories.long_term`: 100
- `limits.memories.history_max`: 1000

### limits.search
- `limits.search.default_limit`: 5
- `limits.search.max_limit`: 100
- `limits.search.vector_dim`: 384

### learning

### learning.reflection
- `learning.reflection.interval`: 5
- `learning.reflection.min_samples`: 10

### learning.dreaming
- `learning.dreaming.interval`: 10
- `learning.dreaming.promotion_threshold`: 0.7

### learning.evolution
- `learning.evolution.interval`: 20
- `learning.evolution.confidence_threshold`: 0.45

### security
- `security.rate_limit`: 100
- `security.max_file_size`: 10485760
- `security.allowed_origins`: ['http://localhost:5011', 'https://localhost:5446']

### paths
- `paths.data`: /mnt/d/clawsjoy_clean/data
- `paths.logs`: /mnt/d/clawsjoy_clean/logs
- `paths.output`: /mnt/d/clawsjoy_clean/output
- `paths.skills`: /mnt/d/clawsjoy_clean/skills
- `paths.models`: /mnt/d/clawsjoy_clean/models
- `paths.ssl`: /mnt/d/clawsjoy_clean/ssl

### models

### models.defaults
- `models.defaults.llm`: qwen2.5:3b
- `models.defaults.embedding`: nomic-embed-text:latest

### models.embedding
- `models.embedding.dimension`: 384

### models.image
- `models.image.default`: sd15
- `models.image.alternatives`: ['dreamshaper']

### engineer
- `engineer.auto_heal_interval`: 600
- `engineer.retry_delay`: 2

### memory_manager
- `memory_manager.default_search_limit`: 5
- `memory_manager.max_search_limit`: 100

### orchestrator
- `orchestrator.short_timeout`: 12
- `orchestrator.normal_timeout`: 30
- `orchestrator.long_timeout`: 90

### capacity
- `capacity.event_queue_maxlen`: 500
- `capacity.message_history_maxlen`: 100
- `capacity.history_max_records`: 1000
- `capacity.vector_dimension`: 384

### success_rate
- `success_rate.high`: 0.9
- `success_rate.medium`: 0.7
- `success_rate.low`: 0.5
- `success_rate.critical`: 0.3

### quality
- `quality.excellent`: 0.8
- `quality.good`: 0.5
- `quality.poor`: 0.3

### resource

### resource.cpu
- `resource.cpu.warning`: 80
- `resource.cpu.critical`: 90

### resource.memory
- `resource.memory.warning`: 80
- `resource.memory.critical`: 90

### resource.disk
- `resource.disk.warning`: 85
- `resource.disk.critical`: 95

## 使用示例

```python
from lib.config_manager import config_manager

# 获取端口
port = config_manager.get_port('gateway')  # 5002

# 获取模型
model = config_manager.get_model()  # qwen2.5:3b

# 获取任意配置
timeout = config_manager.get('timing.timeouts.http', 30)
```