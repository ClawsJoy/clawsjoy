#!/usr/bin/env python3
"""Connection Pool - Connection Pool 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""连接池 - 复用 HTTP 连接"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ConnectionPool:
    """HTTP 连接池"""
    
    _session = None
    
    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()
            # 重试策略
            retry = Retry(total=3, backoff_factor=0.5)
            adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=retry)
            cls._session.mount('http://', adapter)
            cls._session.mount('https://', adapter)
        return cls._session
    
    @classmethod
    def get(cls, url, **kwargs):
        return cls.get_session().get(url, timeout=30, **kwargs)
    
    @classmethod
    def post(cls, url, **kwargs):
        return cls.get_session().post(url, timeout=30, **kwargs)

connection_pool = ConnectionPool()
