#!/bin/bash
cd /home/flybo/clawsjoy_v5
python3 -c "
from core.agents.builtin.collector_agent import collector_agent
collector_agent.run_scheduled_collection()
" >> logs/collector.log 2>&1
