#!/bin/bash
cd /home/flybo/clawsjoy_clean
export PYTHONPATH=/home/flybo/clawsjoy_clean:$PYTHONPATH
export PROJECT_ROOT=/home/flybo/clawsjoy_clean
exec python "$@"
