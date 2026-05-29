#!/bin/bash
cd /home/flybo/clawsjoy_clean
source ~/miniconda3/bin/activate base
gunicorn -c gunicorn_config.py agent_gateway_web:app
