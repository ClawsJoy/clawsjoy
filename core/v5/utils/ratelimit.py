#!/usr/bin/env python3
"""Ratelimit - Ratelimit 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import time
from collections import deque
from threading import Lock
from typing import Dict
from functools import wraps


class RateLimiter:
    """令牌桶限流器"""
    
    def __init__(self, rate: int = 60, capacity: int = 100):
        self.rate = rate  # 每秒令牌数
        self.capacity = capacity  # 桶容量
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()
    
    def acquire(self) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class CircuitBreaker:
    """熔断器 - 防止雪崩"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half_open
        self.lock = Lock()
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.allow_request():
                raise Exception("Circuit breaker is open")

            try:
                result = func(*args, **kwargs)
                self.on_success()
                return result
            except Exception as e:
                self.on_failure()
                raise e

        return wrapper
    
    def allow_request(self) -> bool:
        with self.lock:
            if self.state == "closed":
                return True

            if self.state == "open":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half_open"
                    return True
                return False

            return True
    
    def on_success(self):
        with self.lock:
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
    
    def on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"


class RateLimitMiddleware:
    """限流中间件"""
    
    def __init__(self, default_rate: int = 60):
        self.limiters: Dict[str, RateLimiter] = {}
        self.default_rate = default_rate
    
    def get_limiter(self, user_id: str) -> RateLimiter:
        if user_id not in self.limiters:
            self.limiters[user_id] = RateLimiter(self.default_rate)
        return self.limiters[user_id]
    
    def check(self, user_id: str) -> bool:
        return self.get_limiter(user_id).acquire()


rate_limiter = RateLimitMiddleware()
circuit_breaker = CircuitBreaker()
