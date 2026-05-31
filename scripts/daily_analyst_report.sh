#!/bin/bash
cd /home/flybo/clawsjoy_v5
python3 scripts/analyst_report.py >> logs/analyst_report.log 2>&1
echo "Daily report generated at $(date)" >> logs/daily_report.log
