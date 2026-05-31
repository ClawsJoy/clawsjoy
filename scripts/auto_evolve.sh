#!/bin/bash
cd /home/flybo/clawsjoy_v5
python3 -c "
from core.intelligence.evolution_engine import evolution_engine
evolution_engine.run_evolution()
" >> logs/auto_evolve.log 2>&1
