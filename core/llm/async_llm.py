#!/usr/bin/env python3
"""Async Llm - Async Llm 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time


class AsyncLLMClient:
    """异步 LLM 客户端"""
    
    def __init__(self, max_connections=10):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = config_helper.get_llm_model(fast=True)
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=max_connections)
    
    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_async(self, prompt: str, timeout: int = 30) -> str:
        """异步生成"""
        try:
            session = await self._get_session()
            async with session.post(
                self.ollama_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('response', '')
        except asyncio.TimeoutError:
            return "请求超时，请稍后重试"
        except Exception as e:
            print(f"LLM 异步调用失败: {e}")

        return "服务暂时不可用"
    
    def generate_sync(self, prompt: str, timeout: int = 30) -> str:
        """同步包装"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.generate_async(prompt, timeout))
            loop.close()
            return result
        except:
            return "服务暂时不可用"


async_llm = AsyncLLMClient(max_connections=10)
