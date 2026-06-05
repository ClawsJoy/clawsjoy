#!/usr/bin/env python3
"""Gunicorn Config - Gunicorn Config 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import os

bind = "0.0.0.0:5002"
workers = 2
worker_class = "gevent"
daemon = True
accesslog = "logs/v5_access.log"
errorlog = "logs/v5_error.log"
loglevel = "info"
