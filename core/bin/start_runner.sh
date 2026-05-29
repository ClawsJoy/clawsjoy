#!/bin/bash
cd /mnt/d/clawsjoy_clean
export PYTHONPATH=/mnt/d/clawsjoy_clean:$PYTHONPATH
python3 bin/active_runner.py "$@"
