#!/bin/bash
cd /home/flybo/clawsjoy_v5
celery -A core.lib.celery_app worker --loglevel=info --concurrency=4
