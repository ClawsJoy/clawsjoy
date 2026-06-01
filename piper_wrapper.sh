#!/bin/bash
cd /home/flybo/clawsjoy_v5
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/piper
./piper/piper "$@"
