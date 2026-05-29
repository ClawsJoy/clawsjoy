#!/bin/bash
cd /home/flybo/clawsjoy_clean
pkill -f "ws_asyncio"
sleep 2
python3 ws_asyncio/server.py
